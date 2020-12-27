import configparser
import os.path
import logging
import json
from enum import Enum


def create_config_file(config_path, project_name, source_path):
    template = """
#
# Nedoc configuration file
#

[main]
project_name = {project_name}
project_version = 1.0

source_path = {source_path}
target_path = ./html

# Minimize the resulting HTML files
minimize_output = True


# --- Extra options -----------------------------------------------

# copy_init_docstring = False
# Use __init__ method docstring for class when it does have its own

# markup = rst
# Format docstrings as restructuredText.

# ignore_paths = []
# Use for ignoring files or directories
# E.g.: ignore_paths = ["module1/myfile.py", "module2"]

# create_map_json = True
# Creates mapping "map.json" that contains mapping between
# Python identifiers and documentation

""".format(
        project_name=project_name, source_path=source_path
    )

    with open(config_path, "w") as f:
        f.write(template)


def parse_config(config_path: str):
    config_path = os.path.abspath(config_path)
    config_dir = os.path.dirname(config_path)

    parser = configparser.ConfigParser()
    logging.debug("Reading configuration from %s", config_path)
    with open(config_path) as f:
        parser.read_file(f)
    return parse_config_from_parser(parser, config_dir=config_dir)


def parse_config_from_string(config: str):
    parser = configparser.ConfigParser()
    parser.read_string(config)
    return parse_config_from_parser(parser)


def parse_config_from_parser(parser: configparser.ConfigParser, config_dir=None):
    main = parser["main"]
    config_dir = config_dir or os.getcwd()

    return Config(
        project_name=main["project_name"],
        project_version=main["project_version"],
        source_path=os.path.join(config_dir, main["source_path"]),
        target_path=os.path.join(config_dir, main["target_path"]),
        minimize_output=load_bool(main, "minimize_output", True),
        copy_init_docstring=load_bool(main, "copy_init_docstring", False),
        markup=load_enum(main, "markup", Markup, Markup.NONE),
        style=load_enum(main, "style", DocstringStyle, DocstringStyle.NONE),
        ignore_paths=load_json(main, "ignore_paths", ()),
        create_map_json=load_bool(main, "create_map_json", False),
    )


def load_enum(section, name, enum_type, default):
    value = section.get(name)
    if value is None:
        return default
    try:
        return enum_type(value)
    except ValueError:
        raise Exception(
            "{} have to be one of: {}".format(
                name, ", ".join(v.value for v in enum_type)
            )
        )


def load_bool(section, key, default=True):
    value = section.get(key)
    if value is None:
        return default
    value = value.strip().lower()
    if value not in ("true", "false"):
        raise Exception("{} expects boolean value: True/False".format(key))
    return value == "true"


def load_json(section, key, default=None):
    value = section.get(key)
    if value is None:
        return default
    return json.loads(value)


class DocstringStyle(Enum):

    NONE = "none"
    NUMPY = "numpy"
    RST = "rst"
    GOOGLE = "google"


class Markup(Enum):

    NONE = "none"
    RST = "rst"


class Config:
    def __init__(
        self,
        project_name,
        project_version,
        source_path,
        target_path,
        minimize_output=True,
        copy_init_docstring=False,
        style: DocstringStyle = DocstringStyle.NONE,
        markup: Markup = Markup.NONE,
        ignore_paths=(),
        debug=False,
        create_map_json=False,
    ):
        self.debug = debug
        self.project_name = project_name
        self.project_version = project_version
        self.source_path = source_path
        self.target_path = target_path
        self.ignore_paths = ignore_paths
        self.style = style

        if self.source_path.endswith(os.sep):
            self.source_path = self.source_path[:-1]

        self.minimize_output = minimize_output
        self.copy_init_docstring = copy_init_docstring
        self.markup = markup
        self.create_map_json = create_map_json
