from nedoc.unit import Function
from .utils.project_builder import parse_unit


def test_parse_argument_type(tmp_path):
    fn = parse_unit(tmp_path, """
def target(a: int):
    pass
""")
    assert isinstance(fn, Function)
    assert fn.args[0].annotation == "int"
