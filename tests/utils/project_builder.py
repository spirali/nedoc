from pathlib import Path

from nedoc.config import create_config_file, parse_config
from nedoc.core import Core
from nedoc.markup.md import convert_markdown_to_html
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

    def build(self) -> "BuiltProject":
        conf_path = str(self.root_dir.joinpath("nedoc.conf"))
        create_config_file(conf_path, self.name, ".")
        conf = parse_config(conf_path)
        conf.target_path = str(self.root_dir.joinpath("html"))

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
            cname = (".", )
        else:
            cname = tuple(path.split("."))
        return self.core.gctx.find_by_cname(cname)

    def markdown(self, path: str) -> str:
        """
        Renders the docstring of a unit with the given `path` to Markdown.
        """
        unit = self.get(path)
        return convert_markdown_to_html(self.core.gctx, unit, unit.docstring)
