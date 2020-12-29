import pytest

from nedoc.config import Markup, parse_config_from_string


def with_defaults(text):
    return """
    [main]
    project_name = test
    project_version = 1.0
    source_path = ./
    target_path = doc

    {}""".format(
        text
    )


def test_parse_rst_markup():
    config = parse_config_from_string(
        with_defaults(
            """
    markup = rst
    """
        )
    )

    assert config.markup == Markup.RST


def test_nonexistent_markup():
    with pytest.raises(Exception):
        parse_config_from_string(
            with_defaults(
                """
    markup = foo
    """
            )
        )
