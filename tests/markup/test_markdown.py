from nedoc.config import DocstringStyle, Markup
from ..utils.project_builder import ProjectBuilder, render_docline, render_docstring


def test_markdown_convert(tmp_path, snapshot):
    code = '''
"""
## This is title

This is normal multi-line
paragraph.

**Bold text**

*Italic text*

- Item 1
- Item 2
- Item 3

[Link](url)
"""
'''
    result = ProjectBuilder(tmp_path).file("__init__.py", code).build()
    snapshot.assert_match(result.markdown("src"), "expected.html")


def test_markdown_link_ignore_no_codespan(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [Bar](src.a.bar.Bar)
    """
''',
    )
    pb.file(
        "a/bar.py",
        """
class Bar:
    pass
""",
    )
    result = pb.build()
    x = result.markdown("src.a.foo.Foo")
    assert x == '<p><a href="src.a.bar.Bar">Bar</a></p>\n'


def test_markdown_link_absolute(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [Bar](`src.a.bar.Bar`)
    """
''',
    )
    pb.file(
        "a/bar.py",
        """
class Bar:
    pass
""",
    )
    result = pb.build()
    x = result.markdown("src.a.foo.Foo")
    assert x == '<p><a href="src.a.bar.Bar.html">Bar</a></p>\n'


def test_markdown_link_relative_no_prefix(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "foo.py",
        '''
class Foo:
    """
    [Bar](`Bar`)
    """

class Bar:
    pass
''',
    )
    result = pb.build()
    x = result.markdown("src.foo.Foo")
    assert x == '<p><a href="src.foo.Bar.html">Bar</a></p>\n'


def test_markdown_link_relative_single_dot_prefix(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "foo.py",
        '''
class Foo:
    """
    [Bar](`.Bar`)
    """

class Bar:
    pass
''',
    )
    result = pb.build()
    x = result.markdown("src.foo.Foo")
    assert x == '<p><a href="src.foo.Bar.html">Bar</a></p>\n'


def test_markdown_link_relative_parent_path(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/b/foo.py",
        '''
class Foo:
    """
    [Bar](`...Bar`)
    """
''',
    )
    pb.file(
        "a/__init__.py",
        """
class Bar:
    pass
""",
    )
    result = pb.build()
    x = result.markdown("src.a.b.foo.Foo")
    assert x == '<p><a href="src.a.Bar.html">Bar</a></p>\n'


def test_markdown_link_relative_parent_path_child_module(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/b/foo.py",
        '''
class Foo:
    """
    [Bar](`...bar.Bar`)
    """
''',
    )
    pb.file(
        "a/bar.py",
        """
class Bar:
    pass
""",
    )
    result = pb.build()
    x = result.markdown("src.a.b.foo.Foo")
    assert x == '<p><a href="src.a.bar.Bar.html">Bar</a></p>\n'


def test_markdown_link_module(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "foo.py",
        '''
class Foo:
    """
    [bar](`src.foo`)
    """
''',
    )
    result = pb.build()
    x = result.markdown("src.foo.Foo")
    assert x == '<p><a href="src.foo.html">bar</a></p>\n'


def test_markdown_link_current_module(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "foo.py",
        '''
class Foo:
    """
    [bar](`.`)
    """
''',
    )
    result = pb.build()
    x = result.markdown("src.foo.Foo")
    assert x == '<p><a href="src.foo.html">bar</a></p>\n'


def test_markdown_link_current_module_in_module(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "foo.py",
        '''
"""
[bar](`.`)
"""
''',
    )
    result = pb.build()
    x = result.markdown("src.foo")
    assert x == '<p><a href="src.foo.html">bar</a></p>\n'


def test_markdown_link_class(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "foo.py",
        '''
class Foo:
    """
    [Bar](`src.foo.Bar`)
    """

class Bar:
    pass
''',
    )
    result = pb.build()
    x = result.markdown("src.foo.Foo")
    assert x == '<p><a href="src.foo.Bar.html">Bar</a></p>\n'


def test_markdown_link_function(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "foo.py",
        '''
class Foo:
    """
    [bar](`src.foo.bar`)
    """

    def fn(self):
        pass


def bar():
    pass
''',
    )
    result = pb.build()
    x = result.markdown("src.foo.Foo")
    assert x == '<p><a href="src.foo.html#f_bar">bar</a></p>\n'


def test_markdown_link_method(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "foo.py",
        '''
class Foo:
    """
    [bar](`src.foo.Bar.fn`)
    """


class Bar:
    def fn(self):
        pass
''',
    )
    result = pb.build()
    x = result.markdown("src.foo.Foo")
    assert x == '<p><a href="src.foo.Bar.html#f_fn">bar</a></p>\n'


def test_markdown_link_self_method(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "foo.py",
        '''
class Foo:
    """
    [bar](`fn`)
    """

    def fn(self):
        pass
''',
    )
    result = pb.build()
    x = result.markdown("src.foo.Foo")
    assert x == '<p><a href="src.foo.Foo.html#f_fn">bar</a></p>\n'


def test_markdown_link_prefer_local_over_module_without_dot(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "foo.py",
        '''
class Foo:
    """
    [bar](`Bar`)
    """

    def Bar(self):
        pass


class Bar:
    pass
''',
    )
    result = pb.build()
    x = result.markdown("src.foo.Foo")
    assert x == '<p><a href="src.foo.Foo.html#f_Bar">bar</a></p>\n'


def test_markdown_link_prefer_module_over_local_with_dot(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "foo.py",
        '''
class Foo:
    """
    [bar](`.Bar`)
    """

    def Bar(self):
        pass


class Bar:
    pass
''',
    )
    result = pb.build()
    x = result.markdown("src.foo.Foo")
    assert x == '<p><a href="src.foo.Bar.html">bar</a></p>\n'


def test_markdown_link_missing_parent(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "foo.py",
        '''
"""
[bar](`...Bar`)
"""
''',
    )
    result = pb.build()
    x = result.markdown("src.foo")
    assert x == '<p><a href="%60...Bar%60">bar</a></p>\n'


def test_markdown_in_argument_docstring(tmp_path, snapshot):
    rendered = render_docstring(tmp_path, '''
def target(a: int):
    """
    Documentation.

    :param a: **Markdown** can be used *here*. Also [links](`bar`).
    """

def bar():
    pass
''', style=DocstringStyle.RST, markup=Markup.MARKDOWN)
    snapshot.assert_match(rendered, "expected.html")


def test_markdown_in_docline(tmp_path, snapshot):
    rendered = render_docline(tmp_path, '''
def target(a: int):
    """
    Documentation with **bold text** and a [link](`.bar`).
    """

def bar():
    pass
''', markup=Markup.MARKDOWN)
    snapshot.assert_match(rendered, "expected.html")


def test_markdown_link_module_relative_in_init(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/__init__.py",
        '''
def target():
    """
    [bar](`.bar`)
    """

def bar():
    pass
''',
    )
    result = pb.build()
    x = result.markdown("src.a.target")
    assert x == '<p><a href="src.a.html#f_bar">bar</a></p>\n'


def test_markdown_link_module_relative_in_root_init(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "__init__.py",
        '''
def target():
    """
    [bar](`.bar`)
    """

def bar():
    pass
''',
    )
    result = pb.build()
    x = result.markdown("src.target")
    assert x == '<p><a href="src.html#f_bar">bar</a></p>\n'
