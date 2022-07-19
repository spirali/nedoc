import logging
import multiprocessing
import os
import shutil
import sys

import tqdm

from .parse import construct_module, parse_path
from .render import Renderer, link_to, write_output
from .unit import Class, Module
from .version import VERSION


class GlobalContext:
    def __init__(self, config):
        self.config = config
        self.modules = {}
        self.top_level_names = []
        self.nedoc_version = VERSION

    def get_module(self, cname):
        return self.modules.get(cname)

    def find_by_cname(self, cname):
        module = self.modules.get((cname[0],))
        if module is None:
            return None
        return module.find_by_cname(cname[1:], self)

    def toplevel_modules(self):
        return [module for cname, module in self.modules.items() if len(cname) == 1]

    def get_all_units(self):
        for module in self.toplevel_modules():
            yield from module.traverse()


class NedocException(Exception):
    pass


class Core:
    def __init__(self, config):
        self.gctx = GlobalContext(config)

    def scan_directories(self):
        ignore_paths = self.gctx.config.ignore_paths
        paths = []
        source_path = self.gctx.config.source_path
        parent_path = os.path.dirname(source_path)
        for root, _, files in os.walk(source_path, followlinks=True):
            logging.info("Scanning %s", root)
            path = os.path.relpath(root, parent_path)
            for filename in files:
                if filename.endswith(".py"):
                    fpath = os.path.join(path, filename)
                    for p in ignore_paths:
                        if fpath.startswith(p):
                            logging.debug("Found filename %s, ignoring", fpath)
                            break
                    else:
                        logging.debug("Found filename %s", fpath)
                        paths.append(fpath)
        return paths

    def find_or_create_module(self, cname, is_dir, source_filename):
        module = self.gctx.get_module(cname)
        if module is not None:
            assert module.is_dir == is_dir
            if source_filename:
                module.source_filename = source_filename
            return module
        module = Module(cname[-1], is_dir, source_filename)
        if len(cname) > 1:
            parent = self.find_or_create_module(cname[:-1], True, None)
            parent.add_child(module)
        self.gctx.modules[cname] = module
        return module

    def build_modules(self):
        config = self.gctx.config

        if not os.path.isdir(config.source_path):
            raise NedocException(
                "Source path '{}' is not a directory".format(config.source_path)
            )

        paths = self.scan_directories()

        if not paths:
            raise NedocException(
                "No Python files found in '{}'".format(config.source_path)
            )

        if not os.path.isdir(config.target_path):
            logging.info("Creating directory %s", config.target_path)
            os.makedirs(config.target_path)

        source_path = os.path.dirname(config.source_path)
        fullpaths = (os.path.join(source_path, path) for path in paths)
        #  processed = (parse_path(p) for p in fullpaths)
        pool = multiprocessing.Pool()
        processed = pool.imap(parse_path, fullpaths)
        for path, (atok, code) in tqdm.tqdm(
            zip(paths, processed), total=len(paths), desc="parsing"
        ):
            name_tuple = tuple(path[:-3].split(os.sep))
            is_dir = name_tuple[-1] == "__init__"
            if is_dir:
                name_tuple = name_tuple[:-1]
            module = self.find_or_create_module(name_tuple, is_dir, path)
            module.source_code = code
            construct_module(atok, atok.tree, module)

        for root in self.gctx.toplevel_modules():
            for module in root.traverse():
                module.finalize(self.gctx)

    def build(self):
        self.build_modules()
        self.render()

    def copy_assets(self):
        source = os.path.join(os.path.dirname(__file__), "templates", "assets")
        target = os.path.join(self.gctx.config.target_path, "assets")
        logging.debug("Copying assets from '%s' to '%s'", source, target)

        if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.rmtree(target, ignore_errors=True)
            shutil.copytree(source, target)

    def make_index(self):
        index = os.path.join(self.gctx.config.target_path, "index.html")
        if os.path.isdir(index):
            raise Exception(
                "Trying to create '{}', but it already exists"
                " and it is directory".format(index)
            )
        if os.path.isfile(index):
            logging.debug("Removing old index.html")
            os.unlink(index)

        modules = self.gctx.toplevel_modules()
        module = modules[0]
        target = link_to(module)
        logging.debug("Creating symlink '%s' -> '%s'", index, target)
        try:
            os.symlink(target, index)
        except NotImplementedError:
            logging.warning(
                "Cannot create 'index.html' as symlink, copy is used as fallback"
            )
            logging.debug("Copying file '{}' as 'index.html'".format(index))
            target = os.path.join(self.gctx.config.target_path, target)
            shutil.copyfile(target, index)

    def render(self):
        self.copy_assets()
        renderer = Renderer(self.gctx)
        renderer.render_nedoc_js()
        for root in self.gctx.toplevel_modules():
            units = [
                unit
                for unit in root.traverse()
                if isinstance(unit, Class) or isinstance(unit, Module)
            ]

            pool = multiprocessing.Pool()

            renders = (renderer.render_unit(unit) for unit in units)
            if self.gctx.config.debug:
                writes = (write_output(x) for x in renders)
            else:
                writes = pool.imap_unordered(write_output, renders)

            for unit in tqdm.tqdm(writes, desc="writedoc", total=len(units)):
                pass

            modules = [
                unit
                for unit in units
                if hasattr(unit, "source_code") and unit.source_code
            ]

            renders = (renderer.render_source(unit) for unit in modules)
            if self.gctx.config.debug:
                writes = (write_output(x) for x in renders)
            else:
                writes = pool.imap_unordered(write_output, renders)

            for unit in tqdm.tqdm(writes, desc="writesrc", total=len(modules)):
                pass

        self.make_index()

        if self.gctx.config.create_map_json:
            renderer.render_map_json()
