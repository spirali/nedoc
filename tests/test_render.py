from conftest import load_project


def test_render_args(project1):
    core = load_project(project1)

    fs = core.gctx.find_by_cname(("myproject", "mymodule1", "functions"))
    f = fs.local_find("two_args")
    assert "arg1, next_arg=2" == f.render_args()
