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
    snapshot.assert_match(result.markdown("."), "markdown-0.html")


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
    [`Bar`](a.bar.Bar)
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
    assert x == '<p><a href="a.bar.Bar.html"><code>Bar</code></a></p>\n'


def test_markdown_link_relative_no_prefix(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [`Bar`](Bar)
    """

class Bar:
    pass
''',
    )
    result = pb.build()
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.Bar.html"><code>Bar</code></a></p>\n'


def test_markdown_link_relative_single_dot_prefix(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [`Bar`](.Bar)
    """

class Bar:
    pass
''',
    )
    result = pb.build()
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.Bar.html"><code>Bar</code></a></p>\n'


def test_markdown_link_relative_parent_path(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/b/foo.py",
        '''
class Foo:
    """
    [`Bar`](...Bar)
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
    assert x == '<p><a href="a.Bar.html"><code>Bar</code></a></p>\n'


def test_markdown_link_relative_parent_path_child_module(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/b/foo.py",
        '''
class Foo:
    """
    [`Bar`](...bar.Bar)
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
    assert x == '<p><a href="a.bar.Bar.html"><code>Bar</code></a></p>\n'


def test_markdown_link_class(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [`Bar`](a.foo.Bar)
    """

class Bar:
    pass
''',
    )
    result = pb.build()
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.Bar.html"><code>Bar</code></a></p>\n'


def test_markdown_link_function(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [`bar`](a.foo.bar)
    """

    def fn(self):
        pass


def bar():
    pass
''',
    )
    result = pb.build()
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.html#f_bar"><code>bar</code></a></p>\n'


def test_markdown_link_method(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [`bar`](a.foo.Bar.fn)
    """


class Bar:
    def fn(self):
        pass
''',
    )
    result = pb.build()
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.Bar.html#f_fn"><code>bar</code></a></p>\n'


def test_markdown_link_self_method(tmp_path):
    pb = ProjectBuilder(tmp_path)
    pb.file(
        "a/foo.py",
        '''
class Foo:
    """
    [`bar`](fn)
    """

    def fn(self):
        pass
''',
    )
    result = pb.build()
    x = result.markdown("a.foo.Foo")
    assert x == '<p><a href="a.foo.Foo.html#f_fn"><code>bar</code></a></p>\n'
