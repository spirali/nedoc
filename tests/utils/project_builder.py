from pathlib import Path
from typing import Tuple

from nedoc.config import DocstringStyle, create_config_file, parse_config
from nedoc.core import Core
from nedoc.markup.md import convert_markdown_to_html
from nedoc.render import RenderContext, Renderer
from nedoc.unit import Unit


class ProjectBuilder:
    def __init__(self, path: Path, name="project"):
        self.name = name
        self.root_dir = path.joinpath(name)
        self.root_dir.mkdir(exist_ok=True, parents=True)
        self.dir_stack = [self.root_dir]

    def active_dir(self) -> Path:
        return self.dir_stack[-1]

    def push_dir(self, name: str):
        dir = self.active_dir() / name
        dir.mkdir(exist_ok=True, parents=True)
        self.dir_stack.append(dir)

    def pop_dir(self):
        assert len(self.dir_stack) > 1
        self.dir_stack.pop()

    def file(self, name: str, content: str):
        filepath = self.active_dir().joinpath(name)
        filepath.parent.mkdir(exist_ok=True, parents=True)
        with open(filepath, "w") as f:
            f.write(content)

    def build(self, **config_args) -> "BuiltProject":
        conf_path = str(self.root_dir.joinpath("nedoc.conf"))
        create_config_file(conf_path, self.name, ".")
        conf = parse_config(conf_path)
        conf.target_path = str(self.root_dir.joinpath("html"))

        args = dict(config_args)
        if "style" not in args:
            args["style"] = DocstringStyle.RST
        for (key, value) in args.items():
            setattr(conf, key, value)

        core = Core(conf)
        core.build_modules()
        return BuiltProject(core)


class BuiltProject:
    def __init__(self, core: Core):
        self.core = core

    def get(self, path: str) -> Unit:
        """
        Finds a unit by a dotted path (`a.b.c`).
        """
        if path == ".":
            cname = (".",)
        else:
            cname = tuple(path.split("."))
        return self.core.gctx.find_by_cname(cname)

    def markdown(self, path: str) -> str:
        """
        Renders the docstring of a unit with the given `path` to Markdown.
        """
        unit = self.get(path)
        return convert_markdown_to_html(self.core.gctx, unit, unit.docstring)


def parse_unit(tmpdir: Path, code: str, name="target", **config_args) -> Unit:
    return parse_unit_inner(tmpdir, code, name, **config_args)[1]


def parse_unit_inner(
    tmpdir: Path, code: str, name: str, **config_args
) -> Tuple[BuiltProject, Unit]:
    pb = ProjectBuilder(tmpdir)
    pb.file("a/foo.py", code)
    built = pb.build(**config_args)
    return (built, built.get(f"a.foo.{name}"))


def render_docstring(tmpdir: Path, code: str, name="target", **config_args) -> str:
    built, unit = parse_unit_inner(tmpdir, code, name=name, **config_args)

    renderer = Renderer(built.core.gctx)
    template = renderer.lookup.get_template("docstring.mako")

    render_ctx = RenderContext(unit, built.core.gctx)
    return template.get_def("render_docstring").render(render_ctx, unit)
