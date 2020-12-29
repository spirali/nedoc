import typing

import docstring_parser

from .config import DocstringStyle

STYLE_MAP = {
    DocstringStyle.NUMPY: docstring_parser.Style.numpydoc,
    DocstringStyle.RST: docstring_parser.Style.rest,
    DocstringStyle.GOOGLE: docstring_parser.Style.google,
}


class ParsedDocString:
    def __init__(
        self,
        docline: typing.Union[str, None],
        description: typing.Union[str, None],
        params=None,
        returns=None,
        raises=None,
        subsections=None,
    ):
        self.docline = docline
        self.description = description
        self.params = params
        self.returns = returns
        self.raises = raises
        self.subsections = subsections

    def has_more(self) -> bool:
        return bool(
            self.description
            or self.params
            or self.returns
            or self.raises
            or self.subsections
        )


def merge_first_line(docstring: str) -> str:
    lines = docstring.split("\n")
    for i, line in enumerate(lines):
        if not line.strip():
            break
    else:
        if len(lines) > 3:
            return docstring
        else:
            return " ".join(lines)
    if i > 3:
        return docstring
    return " ".join(line.strip() for line in lines[:i]) + "\n" + "\n".join(lines[i:])


def parse_docstring(
    style: DocstringStyle, docstring: typing.Union[str, None]
) -> ParsedDocString:

    if docstring is None:
        return ParsedDocString(None, None)

    docstring = merge_first_line(docstring.strip())

    ds_style = STYLE_MAP.get(style)
    if not ds_style:  # None style
        lines = docstring.split("\n", 1)
        if len(lines) == 1:
            docline = lines[0]
            description = None
        else:
            docline, description = lines
            description = description.lstrip()
        return ParsedDocString(docline, description)

    dstr = docstring_parser.parse(docstring, ds_style)
    subsections = [
        (m.args[0].replace("_", " ").capitalize(), m.description)
        for m in dstr.meta
        if len(m.args) == 1 and m.args[0] not in ("param", "returns", "raises")
    ]
    return ParsedDocString(
        dstr.short_description,
        dstr.long_description,
        dstr.params,
        dstr.returns,
        dstr.raises,
        subsections,
    )


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
