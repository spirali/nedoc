from nedoc.markup.md import convert_markdown_to_html


def test_markdown_convert(snapshot):
    text = """

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

    result = convert_markdown_to_html(text)
    snapshot.assert_match(result, "markdown-0.html")
