from .utils.project_builder import parse_unit, render_docstring


def test_render_fn_args_multiple(tmp_path):
    fn = parse_unit(
        tmp_path,
        """
def target(arg1, next_arg=2):
    pass
""",
    )
    assert fn.render_args() == "arg1, next_arg=2"


def test_render_fn_args_star(tmp_path):
    fn = parse_unit(
        tmp_path,
        """
def target(x1, x2, *, y1=0):
    pass
""",
    )
    assert fn.render_args() == "x1, x2, *, y1=0"


def test_render_fn_args_star2(tmp_path):
    fn = parse_unit(
        tmp_path,
        """
def target(x1, x2, *ags, mm=1, **keywords):
    pass
""",
    )
    assert fn.render_args() == "x1, x2, *ags, mm=1, **keywords"


def test_render_docstring_take_argument_type_from_type_hint(tmp_path, snapshot):
    rendered = render_docstring(
        tmp_path,
        '''
def target(a: int, b: str):
    """
    Some documentation.

    :param a: a first argument
    :param b: a second argument
    """
    pass
''',
    )
    snapshot.assert_match(rendered, "expected.html")


def test_render_docstring_take_kwonly_argument_type_from_type_hint(tmp_path, snapshot):
    rendered = render_docstring(
        tmp_path,
        '''
def target(a: int, *, b: str):
    """
    Some documentation.

    :param a: a first argument
    :param b: a second argument
    """
    pass
''',
    )
    snapshot.assert_match(rendered, "expected.html")
