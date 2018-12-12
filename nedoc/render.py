import datetime
import itertools
import json
import os

import htmlmin
import mako.lookup
from mako.filters import html_escape

from .unit import Module, Function, Class, UnitChild


#  from .rst import convert_rst_to_html


class RenderContext:

    def __init__(self, unit, gctx):
        self.unit = unit
        self.gctx = gctx
        self.now = datetime.datetime.now()

    def link_to(self, unit):
        return unit.fullname + ".html"

    def link_to_cname(self, cname, absolute=False):
        if absolute:
            unit = self.gctx.find_by_cname(cname)
        else:
            unit = self.unit.module().find_by_cname(cname, self.gctx)
        if unit is None:
            return None
        return self.link_to(unit)

    def link_to_source(self, unit):
        if unit.source_filename is None:
            return None
        return "source+{}.html".format(
            unit.source_filename.replace(os.sep, "."))

    def format_code(self, code):
        from pygments.formatters import HtmlFormatter
        from pygments import lexers
        from pygments import highlight

        formatter = HtmlFormatter(linenos=True)
        lexer = lexers.get_lexer_by_name("python")
        return highlight(code, lexer, formatter)

    def render_docstring(self, unit):
        return "<pre>{}</pre>".format(html_escape(unit.docstring))
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
                          for uc in u.all_units(gctx, public=public)]
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

    def render_tree_js(self, units):
        def get_all(unit):
            return [item for item in unit.traverse() if not isinstance(item, Function)]

        ctx = RenderContext(None, self.gctx)
        modules = (((child.fullname, ctx.link_to(child)) for child in get_all(unit))
                   for unit in units)
        modules = sorted(set(itertools.chain.from_iterable(modules)))
        path = os.path.abspath(os.path.join(self.gctx.config.target_path, "modules.js"))

        with open(path, "w") as f:
            f.write("var NEDOC_MODULES = JSON.parse('{}');\n".format(json.dumps(modules)))

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
        output = htmlmin.minify(output, remove_empty_space=True)
    with open(path, "w") as f:
        f.write(output)
