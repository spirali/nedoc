import datetime
import json
import os

import htmlmin
import mako.lookup
from mako.filters import html_escape

from .config import Markup
from .docstring import ParsedDocString, parse_docstring
from .markup.rst import convert_rst_to_html
from .unit import Class, Function, Module, Unit, UnitChild


def link_to(unit: Unit) -> str:
    if isinstance(unit, Function):
        return unit.parent.fullname.replace(" ", "_") + ".html#f_" + unit.name
    else:
        return unit.fullname.replace(" ", "_") + ".html"


class RenderContext:
    def __init__(self, unit: Unit, gctx):
        self.unit = unit
        self.gctx = gctx
        self.now = datetime.datetime.now()

    def link_to(self, unit):
        return link_to(unit)

    def link_to_cname(self, cname, absolute=False):
        if absolute:
            unit = self.gctx.find_by_cname(cname)
        else:
            unit = self.unit.module().find_by_cname(cname, self.gctx)
        if unit is None:
            return None
        return self.link_to(unit)

    def link_to_source(self, unit):
        module = unit.module()
        if module.source_filename is None:
            return None
        source_filename = module.source_filename
        source_filename = source_filename.replace(os.sep, ".")
        source_filename = source_filename.replace(" ", "_")
        url = "source+{}.html".format(source_filename)
        if unit.lineno is None:
            return url
        else:
            return "{}#line-{}".format(url, unit.lineno - 1)

    def format_code(self, code):
        from pygments import highlight, lexers
        from pygments.formatters import HtmlFormatter

        formatter = HtmlFormatter(linenos=True, lineanchors="line")
        lexer = lexers.get_lexer_by_name("python")
        return highlight(code, lexer, formatter)

    def render_paragraph(self, text):
        if self.gctx.config.markup == Markup.RST:
            content = convert_rst_to_html(text)
            return "<div class='rst-doc'>{}</div>".format(content)
        if self.gctx.config.markup == Markup.MARKDOWN:
            from .markup.md import convert_markdown_to_html

            content = convert_markdown_to_html(self.gctx, self.unit, text)
            return "<div class='md-doc'>{}</div>".format(content)
        else:
            escaped = html_escape(text)
            return "<pre>{}</pre>".format(escaped)

    def get_parsed_docstring(self, unit: Unit) -> ParsedDocString:
        docstring = parse_docstring(self.gctx.config.style, unit.docstring)
        return enrich_docstring_with_type_hints(docstring, unit)


def enrich_docstring_with_type_hints(
    docstring: ParsedDocString, unit: Unit
) -> ParsedDocString:
    if isinstance(unit, Function):
        args = {arg.name: arg for arg in unit.named_args}
        if docstring.params is not None:
            for param in docstring.params:
                arg = args.get(param.arg_name)
                if arg is not None:
                    if param.type_name is None and arg.annotation is not None:
                        param.type_name = arg.annotation
    return docstring


TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


class Renderer:
    def __init__(self, gctx):
        self.gctx = gctx
        self.lookup = mako.lookup.TemplateLookup(
            [TEMPLATE_DIR],
            default_filters=["html_escape"],
            imports=["from mako.filters import html_escape"],
        )
        self.templates = {}
        self.templates[Module] = self.lookup.get_template("module.mako")
        self.templates[Function] = self.lookup.get_template("function.mako")
        self.templates[Class] = self.lookup.get_template("class.mako")
        self.templates["source"] = self.lookup.get_template("source.mako")

    def tree(self, gctx, unit, public=True):
        out = []
        prev = None
        for u in reversed(unit.path):
            new_result = [
                (1, uc)
                for uc in u.all_units(gctx, public=public)
                if uc.unit.role != "function"
            ]
            new_result.sort(
                key=lambda t: (t[1].unit.sort_order, t[1].imported, t[1].name)
            )
            if prev is not None:
                idx = 0
                for idx, (level, uc) in enumerate(new_result):
                    if uc.unit == prev:
                        break
                new_result[idx + 1 : idx + 1] = [(level + 1, uc) for (level, uc) in out]
            out = new_result
            prev = u

        result = []
        for unit in sorted(self.gctx.toplevel_modules(), key=lambda u: u.name):
            result.insert(0, (0, UnitChild(unit.name, unit, False)))
            if unit == prev:
                result += out
        return result

    def render_unit(self, unit):
        ctx = RenderContext(unit, self.gctx)
        path = os.path.join(self.gctx.config.target_path, ctx.link_to(unit))
        return (
            path,
            self._render(self.templates[type(unit)], ctx, unit),
            self.gctx.config.minimize_output,
        )

    def render_source(self, unit):
        ctx = RenderContext(unit, self.gctx)
        path = os.path.join(self.gctx.config.target_path, ctx.link_to_source(unit))
        return (
            path,
            self._render(self.templates["source"], ctx, unit),
            self.gctx.config.minimize_output,
        )

    def render_nedoc_js(self):
        modules = [
            (unit.name, unit.parent.fullname, not isinstance(unit, Function))
            for unit in self.gctx.get_all_units()
            if unit.parent
        ]
        modules.sort()

        template = os.path.join(os.path.dirname(__file__), "templates/nedoc.js")
        path = os.path.abspath(os.path.join(self.gctx.config.target_path, "nedoc.js"))

        with open(template) as f:
            content = f.read()
        with open(path, "w") as f:
            f.write(content.replace("%MODULES%", json.dumps(modules)))

    def render_map_json(self):
        path = os.path.abspath(os.path.join(self.gctx.config.target_path, "map.json"))
        units = {unit.fullname: link_to(unit) for unit in self.gctx.get_all_units()}
        with open(path, "w") as f:
            f.write(json.dumps(units))

    def _render(self, template, ctx, unit):
        return template.render(
            gctx=self.gctx,
            unit=unit,
            tree=self.tree,
            render_cname=lambda cname: ".".join(cname),
            ctx=ctx,
        )


def write_output(conf):
    path, output, minimize = conf
    if minimize:
        output = htmlmin.minify(output, remove_empty_space=True, remove_comments=True)
    with open(path, "w") as f:
        f.write(output)
