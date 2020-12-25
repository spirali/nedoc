from mako.filters import html_escape
from nedoc.rst import convert_rst_to_html
from .config import Config
import docstring_parser


class ParsedDocString:

    def __init__(self, docline, description, params, returns, raises, subsections):
        self.docline = docline
        self.description = description
        self.params = params
        self.returns = returns
        self.raises = raises
        self.subsections = subsections

    def has_more(self):
        return bool(self.description or self.params or self.returns or self.raises or self.subsections)


def parse_docstring(config: Config, docstring: str) -> ParsedDocString:
    style = docstring_parser.Style.numpydoc
    dstr = docstring_parser.parse(docstring, style)

    subsections = [
        (m.args[0].replace("_", " ").capitalize(), m.description)
        for m in dstr.meta
        if len(m.args) == 1 and m.args[0] not in ("param", "returns", "raises")
    ]

    return ParsedDocString(dstr.short_description,
                           dstr.long_description,
                           dstr.params,
                           dstr.returns,
                           dstr.raises, subsections)


def get_simple_docline(docstring):
    if not docstring:
        return ""
    lines = docstring.strip().split("\n")
    result = []
    for line in lines[:3]:  # max 3 lines
        line = line.strip()
        if not line:
            return " ".join(result)
        result.append(line)
    return " ".join(result)
