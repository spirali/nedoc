<%namespace file="utils.mako" import="link_to_unit, link_to_source, symbol_link"/>
<%inherit file="base.mako" />

## -- Header --
<h1>${"Method" if unit.is_method else "Function"} ${unit.name}</h1>
In ${link_to_unit(unit.parent)}

<p>${unit.docline}</p>

## -- Declaration --
<h2>Declaration</h2>
<% arg_style = {
    "self_style": ("<span class='kw'>", "</span>"),
    "default_style": ("<i>", "</i>")
}
%>
<div class="decl">
%if len(unit.args) <= 1:
    <div class="def"><span class="kw">def</span> ${unit.name}(<span class="args">${unit.render_args(**arg_style) | n}</span>):
    <div class="idnt">${link_to_source(unit, "source code")}</div>
    </div>
%else:
    <div class="def"><span class="kw">def</span> ${unit.name}(
    % for arg in unit.args:
    <div class="args" style="padding-left: 2em">${arg.render(**arg_style) | n}${"," if not loop.last else ""}</div>
    % endfor
    ):
    <div class="idnt">${link_to_source(unit, "source code")}</div>
    </div>
%endif
</div>
% if unit.overrides:
<p>This method overrides ${link_to_unit(unit.overrides)}.</p>
% endif

## -- Documentation
% if unit.docstring:
<h2>Documentation</h2>
${ctx.render_docstring(unit) | n}
% elif unit.overrides and unit.overrides.docstring:
<span class="label">inherited documentation</span>
${ctx.render_docstring(unit.overrides) | n}
%endif

## -- Overrides
% if unit.overriden_by:
<h2>Overrides</h2>
<p>This method is overriden by:
% for u in unit.overriden_by:
    <li>${link_to_unit(u)}</li>
% endfor
</p>
% endif

## Aliases
%if unit.aliases:
<h2>Reexports</h2>
<ul class="deflst">
% for alias in sorted(unit.aliases):
<li>
    %if alias[-1] != unit.name:
    Imported in ${symbol_link(alias[:-1], True)} as ${alias[-1]}.
    %else:
    Imported in ${symbol_link(alias[:-1], True)}.
    %endif
</li>
% endfor
</ul>
%endif
