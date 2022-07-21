from nedoc.unit import Function

from .utils.project_builder import parse_unit


def test_parse_fn_argument_type(tmp_path):
    fn = parse_unit(
        tmp_path,
        """
def target(a: int):
    pass
""",
    )
    assert isinstance(fn, Function)
    assert fn.args[0].annotation == "int"


def test_parse_fn_arguments(tmp_path):
    fn = parse_unit(
        tmp_path,
        """
def target(a, b, c):
    pass
""",
    )
    assert isinstance(fn, Function)
    assert fn.args[0].name == "a"
    assert fn.args[1].name == "b"
    assert fn.args[2].name == "c"


def test_parse_fn_name(tmp_path):
    fn = parse_unit(
        tmp_path,
        """
def foo():
    pass
""",
        name="foo",
    )
    assert isinstance(fn, Function)
    assert fn.name == "foo"
