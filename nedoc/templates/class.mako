<%namespace file="utils.mako" import="symbol_link, link_to_source, link_to_unit"/>
<%inherit file="base.mako" />

## Header
<h1>Class ${unit.name}</h1>
In ${link_to_unit(unit.parent)}

<p>${unit.docline}</p>

## Declaration
<h2>Declaration</h2>
<div class="decl">
<span class="kw">class</span> ${unit.name}\
%if unit.bases:
(\
% for base in unit.bases:
${symbol_link(base)}${"" if loop.last else ", "}\
% endfor
)\
%endif
:
<div class="idnt">${link_to_source(unit, "source code")}</div>
</div>

## Methods
% if unit.functions:
<h2>Methods</h2>
<ul class="deflst">
% for child in unit.functions(public=True):
    <li><div class="def">def <a class="symbol" href="${ctx.link_to(child)}">${child.name}</a>(<span class="args">${child.render_args()}</span>)
        % if child.overrides:
        <span class="label">override<span>
        % endif
        </div>
        % if child.docline:
        <div class="docline">${child.docline}</div>
        % elif child.overrides and child.overrides.docline:
        <div class="docline"><span class="label">inherited doc</span> ${child.overrides.docline}</div>
        % endif
        </li>
% endfor
</ul>
% endif

## Inherited methods
<% im = unit.inherited_methods(ctx.gctx, public=True) %>
% if im:
<h2>Inherited methods</h3>
<ul class="deflst">
%for u, methods in im:
<li><div>Methods inherited from ${link_to_unit(unit)}:</div>
<div>
% for m in methods:
${link_to_unit(m, True)}${"" if loop.last else ", "}\
% endfor
</div>\
% endfor
</ul>
% endif

## Documentation
% if unit.docstring:
<h2>Documentation</h2>
${ctx.render_docstring(unit) | n}
% endif


## Aliases
%if unit.aliases:
<h2>Reexports</h2>
<ul class="deflst">
% for alias in unit.aliases:
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
