from nedoc.core import Core
from nedoc.config import create_config_file, Config


def load_project(project):
    conf_path = str(project.join("nedoc.conf"))
    create_config_file(conf_path, "Project1", "myproject")
    conf = Config(conf_path)
    core = Core(conf)
    core.build_modules()
    return core


def test_render_args(project1):
    core = load_project(project1)

    fs = core.gctx.find_by_cname(("myproject", "mymodule1", "functions"))
    f = fs.local_find("two_args")
    assert "arg1, next_arg=2" == f.render_args()