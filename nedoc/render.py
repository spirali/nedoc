import datetime
import json
import os

import htmlmin
import mako.lookup
from mako.filters import html_escape

from .unit import Module, Function, Class, UnitChild, Unit


#  from .rst import convert_rst_to_html

def link_to(unit):
    if isinstance(unit, Function):
        return unit.parent.fullname + ".html#f_" + unit.name
    else:
        return unit.fullname + ".html"


class RenderContext:

    def __init__(self, unit, gctx):
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
        url = "source+{}.html".format(
            module.source_filename.replace(os.sep, "."))
        if unit.lineno is None:
            return url
        else:
            return "{}#line-{}".format(url, unit.lineno - 1)

    def format_code(self, code):
        from pygments.formatters import HtmlFormatter
        from pygments import lexers
        from pygments import highlight

        formatter = HtmlFormatter(linenos=True, lineanchors="line")
        lexer = lexers.get_lexer_by_name("python")
        return highlight(code, lexer, formatter)

    def render_docstring(self, unit_or_docstring):
        if isinstance(unit_or_docstring, Unit):
            docstring = unit_or_docstring.docstring
        elif isinstance(unit_or_docstring, str):
            docstring = unit_or_docstring
        else:
            assert 0
        return "<pre>{}</pre>".format(html_escape(docstring))
        #  return convert_rst_to_html(
        #  unit.docstring, unit.module().source_filename)

    def render_docline(self, unit):
        return unit.docline


class Renderer:

    def __init__(self, gctx):
        self.gctx = gctx
        paths = [os.path.join(os.path.dirname(__file__), "templates")]
        lookup = mako.lookup.TemplateLookup(
            paths,
            default_filters=['html_escape'],
            imports=['from mako.filters import html_escape'])
        self.templates = {}
        self.templates[Module] = lookup.get_template("module.mako")
        self.templates[Function] = lookup.get_template("function.mako")
        self.templates[Class] = lookup.get_template("class.mako")
        self.templates["source"] = lookup.get_template("source.mako")

    def tree(self, gctx, unit, public=True):
        out = []
        prev = None
        for u in reversed(unit.path):
            new_result = [(1, uc)
                          for uc in u.all_units(gctx, public=public)
                          if uc.unit.role != "function"]
            new_result.sort(
                key=lambda t: (t[1].unit.sort_order, t[1].imported, t[1].name))
            if prev is not None:
                idx = 0
                for idx, (level, uc) in enumerate(new_result):
                    if uc.unit == prev:
                        break
                new_result[idx+1:idx+1] = [(level + 1, uc)
                                           for (level, uc) in out]
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
        return (path,
                self._render(self.templates[type(unit)], ctx, unit),
                self.gctx.config.minimize_output)

    def render_source(self, unit):
        ctx = RenderContext(unit, self.gctx)
        path = os.path.join(
            self.gctx.config.target_path, ctx.link_to_source(unit))
        return (path,
                self._render(self.templates["source"], ctx, unit),
                self.gctx.config.minimize_output)

    def render_nedoc_js(self):
        modules = [(unit.name, unit.parent.fullname, not isinstance(unit, Function))
                   for unit in self.gctx.get_all_units()
                   if unit.parent]
        modules.sort()

        template = os.path.join(os.path.dirname(__file__), "templates/nedoc.js")
        path = os.path.abspath(os.path.join(self.gctx.config.target_path, "nedoc.js"))

        with open(template) as f:
            content = f.read()
        with open(path, "w") as f:
            f.write(content.replace("%MODULES%", json.dumps(modules)))

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
