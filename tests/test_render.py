
def test_render_args(module1):
    assert module1.childs[0].render_args() == "a, b=5"
