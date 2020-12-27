from nedoc.config import DocstringStyle
from nedoc.docstring import merge_first_line, parse_docstring
import pytest


def test_merge_first_list():
    assert merge_first_line("test1") == "test1"
    assert merge_first_line("test1\n") == "test1\n"
    assert merge_first_line("test1\n\ntest2") == "test1\n\ntest2"
    assert merge_first_line("test1\ntest2\n") == "test1 test2\n"
    assert merge_first_line("test1\ntest2\ntest3\n") == "test1 test2 test3\n"
    assert merge_first_line("test1\ntest2\ntest3") == "test1 test2 test3"
    assert merge_first_line("test1\ntest2\n \ntest3") == "test1 test2\n \ntest3"
    assert merge_first_line("test1\ntest2\n\ntest3") == "test1 test2\n\ntest3"
    assert (
        merge_first_line("test1\ntest2\ntest3\ntest4") == "test1\ntest2\ntest3\ntest4"
    )
    assert (
        merge_first_line("test1\n\ntest2\ntest3\ntest4")
        == "test1\n\ntest2\ntest3\ntest4"
    )
    assert (
        merge_first_line("test1\ntest2\ntest3\n\ntest4\ntest5")
        == "test1 test2 test3\n\ntest4\ntest5"
    )
    assert (
        merge_first_line("test1\ntest2\ntest3\n\ntest4\ntest5\n")
        == "test1 test2 test3\n\ntest4\ntest5\n"
    )


def _normalize_array(value):
    if value is None:
        return []
    return value


def _check_ds(ds, docline=None, description=None, params=0):
    assert ds.docline == docline
    assert ds.description == description
    assert len(_normalize_array(ds.params)) == params


@pytest.mark.parametrize("style", [DocstringStyle.NONE, DocstringStyle.NUMPY])
def test_parse_docstring_basic(style):
    ds = parse_docstring(style, None)
    _check_ds(ds)

    ds = parse_docstring(style, "xxx\n\nhello\nworld!")
    _check_ds(ds, "xxx", "hello\nworld!")

    ds = parse_docstring(style, "xxx\nyyy\n\nhello\nworld!")
    _check_ds(ds, "xxx yyy", "hello\nworld!")

    text = """
xxx
yyy

Parameters
----------
x: int
    Nice property
y: float"""
    ds = parse_docstring(style, text)
    if style == DocstringStyle.NONE:
        _check_ds(ds, "xxx yyy", text[10:])
    if style == DocstringStyle.NUMPY:
        _check_ds(ds, "xxx yyy", None, params=2)
        assert ds.params[0].arg_name == "x"
        assert ds.params[0].type_name == "int"
        assert ds.params[1].arg_name == "y"
