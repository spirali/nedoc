from ..utils.project_builder import ProjectBuilder


def test_markdown_convert(tmp_path, snapshot):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "__init__.py",
        '''
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
    ''',
    )

    result = pb.build()
    snapshot.assert_match(result.markdown("."), "expected.html")


def test_markdown_link_ignore_no_codespan(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [Bar](a.bar.Bar)
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
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.bar.Bar">Bar</a></p>\n'


def test_markdown_link_absolute(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [Bar](`a.bar.Bar`)
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
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.bar.Bar.html">Bar</a></p>\n'


def test_markdown_link_relative_no_prefix(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
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
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.Bar.html">Bar</a></p>\n'


def test_markdown_link_relative_single_dot_prefix(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
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
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.Bar.html">Bar</a></p>\n'


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
    x = result.markdown("a.b.foo.Foo")
    assert x == '<p><a href="a.Bar.html">Bar</a></p>\n'


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
    x = result.markdown("a.b.foo.Foo")
    assert x == '<p><a href="a.bar.Bar.html">Bar</a></p>\n'


def test_markdown_link_module(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [bar](`a.foo`)
    """
''',
    )
    result = pb.build()
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.html">bar</a></p>\n'


def test_markdown_link_current_module(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [bar](`.`)
    """
''',
    )
    result = pb.build()
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.html">bar</a></p>\n'


def test_markdown_link_current_module_in_module(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
"""
[bar](`.`)
"""
''',
    )
    result = pb.build()
    x = result.markdown("a.foo")
    assert x == '<p><a href="a.foo.html">bar</a></p>\n'


def test_markdown_link_class(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [Bar](`a.foo.Bar`)
    """

class Bar:
    pass
''',
    )
    result = pb.build()
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.Bar.html">Bar</a></p>\n'


def test_markdown_link_function(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [bar](`a.foo.bar`)
    """

    def fn(self):
        pass


def bar():
    pass
''',
    )
    result = pb.build()
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.html#f_bar">bar</a></p>\n'


def test_markdown_link_method(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [bar](`a.foo.Bar.fn`)
    """


class Bar:
    def fn(self):
        pass
''',
    )
    result = pb.build()
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.Bar.html#f_fn">bar</a></p>\n'


def test_markdown_link_self_method(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
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
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.Foo.html#f_fn">bar</a></p>\n'


def test_markdown_link_prefer_local_over_module_without_dot(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
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
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.Foo.html#f_Bar">bar</a></p>\n'


def test_markdown_link_prefer_module_over_local_with_dot(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
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
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.Bar.html">bar</a></p>\n'
