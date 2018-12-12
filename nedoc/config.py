import configparser
import os.path


def create_config_file(config_path, project_name, source_path):
    template = """
# nedoc configuration file
[main]
project_name = {project_name}
project_version = 1.0

source_path = {source_path}
target_path = ./html

minimize_output = True
""".format(project_name=project_name, source_path=source_path)

    with open(config_path, "w") as f:
        f.write(template)


class Config:


    def __init__(self, config_path):
        self.debug = False
        config_path = os.path.abspath(config_path)
        config_dir = os.path.dirname(config_path)

        parser = configparser.ConfigParser()
        with open(config_path) as f:
            parser.read_file(f)
        main = parser["main"]

        self.project_name = main["project_name"]
        self.project_version = main["project_version"]
        self.source_path = os.path.join(config_dir, main["source_path"])
        self.target_path = os.path.join(config_dir, main["target_path"])

        if self.source_path.endswith(os.sep):
            self.source_path = self.source_path[:-1]

        minimize = main.get("minimize_output", "true").strip().lower()
        if minimize not in ("true", "false"):
            raise Exception("Minize output expects boolean value: True/False")
        self.minimize_output = minimize == "true"
