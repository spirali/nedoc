import argparse
from . import config, core
from . import version

import os
import sys
import logging


def parse_args():
    parser = argparse.ArgumentParser(
        "nedoc", description='Python documentation generator')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {}'.format(version.VERSION))
    ps = parser.add_subparsers(help="Command", dest="command")
    p = ps.add_parser("build")
    p.add_argument("--debug", default=False, action="store_true")

    p = ps.add_parser("init")
    p.add_argument("project_name")
    p.add_argument("source_path")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.command == "init":
        path = "./nedoc.conf"
        if os.path.isfile(path):
            sys.stderr.write(
                "Error: Configuration file '{}' already exists\n".format(path))
            sys.exit(1)
        if os.path.isdir(path):
            sys.stderr.write(
                "Error: Path '{}' is directory\n".format(path))
            sys.exit(1)

        print("Creating nedoc.conf ...")
        config.create_config_file(
            "./nedoc.conf", args.project_name, args.source_path)

    if args.command == "build":
        if args.debug:
            logging.basicConfig(level=logging.DEBUG)
            logging.info("Debug mode enabled")

        path = "./nedoc.conf"
        if not os.path.isfile(path):
            if os.path.isdir(path):
                sys.stderr.write("Error: Path '{}' is directory")
            else:
                sys.stderr.write(
                    "Error: Configuration file '{}' was not found\n"
                    .format(path))
            sys.exit(1)

        conf = config.parse_config(path)
        conf.debug = args.debug

        if conf.source_path.endswith("."):
            sys.stderr.write("Error: Source directory cannot end by '.'\n")
            sys.exit(1)

        c = core.Core(conf)
        c.build()
