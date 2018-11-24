import os
import logging
import distutils.dir_util
import tqdm

from .unit import Module
from .parse import construct_module, parse_path
from .render import Renderer, write_output

import multiprocessing


class GlobalContext:

    def __init__(self, config):
        self.config = config
        self.modules = {}
        self.top_level_names = []

    def get_module(self, cname):
        return self.modules.get(cname)

    def find_by_cname(self, cname):
        module = self.modules.get((cname[0],))
        if module is None:
            return None
        return module.find_by_cname(cname[1:], self)

    def toplevel_modules(self):
        return [module for cname, module in self.modules.items()
                if len(cname) == 1]


class Core:

    def __init__(self, config):
        self.gctx = GlobalContext(config)

    def scan_directories(self):
        paths = []
        source_path = self.gctx.config.source_path
        parent_path = os.path.dirname(source_path)
        for root, _, files in os.walk(source_path, followlinks=True):
            logging.info("Scanning %s", root)
            path = os.path.relpath(root, parent_path)
            for filename in files:
                if filename.endswith(".py"):
                    logging.debug("Found filename %s", filename)
                    paths.append(os.path.join(path, filename))
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
        source_path = os.path.dirname(config.source_path)
        paths = self.scan_directories()

        if not os.path.isdir(config.target_path):
            logging.info("Creating directory %s", config.target_path)
            os.makedirs(config.target_path)

        fullpaths = (os.path.join(source_path, path) for path in paths)
        #  processed = (parse_path(p) for p in fullpaths)
        pool = multiprocessing.Pool()
        processed = pool.imap(parse_path, fullpaths)
        for path, (atok, code) in tqdm.tqdm(
                zip(paths, processed), total=len(paths), desc="parsing"):
            name_tuple = tuple(path[:-3].split(os.sep))
            is_dir = name_tuple[-1] == "__init__"
            if is_dir:
                name_tuple = name_tuple[:-1]
            module = self.find_or_create_module(name_tuple, is_dir, path)
            module.source_code = code
            construct_module(atok, atok.tree, module)

        for root in self.gctx.toplevel_modules():
            for module in root.travese():
                module.finalize(self.gctx)

    def build(self):
        self.build_modules()
        self.render()

    def copy_assets(self):
        source = os.path.join(os.path.dirname(__file__), "templates", "assets")
        distutils.dir_util.copy_tree(
            source, os.path.join(self.gctx.config.target_path, "assets"))

    def render(self):
        self.copy_assets()
        renderer = Renderer(self.gctx)
        for root in self.gctx.toplevel_modules():
            units = list(root.travese())

            pool = multiprocessing.Pool()

            renders = (renderer.render_unit(unit) for unit in units)
            writes = pool.imap_unordered(write_output, renders)

            for unit in tqdm.tqdm(writes, desc="writedoc", total=len(units)):
                pass

            modules = [unit for unit in units if hasattr(unit, "source_code") and unit.source_code]
            renders = (renderer.render_source(unit) for unit in modules)
            writes = pool.imap_unordered(write_output, renders)

            for unit in tqdm.tqdm(writes, desc="writesrc", total=len(modules)):
                pass
