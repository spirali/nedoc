from nedoc.rst import convert_rst_to_html


def test_rst_convert():
    text = """

This is title
=============

This is normal multi-line
paragraph.

Next title
=========

    """

    result = convert_rst_to_html(text)
    assert "<h3>This is title</h3>" in result
