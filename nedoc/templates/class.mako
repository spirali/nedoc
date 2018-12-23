<%namespace file="utils.mako" import="symbol_link, link_to_source, link_to_unit"/>
<%namespace file="function.mako" import="function_desc"/>
<%inherit file="base.mako" />

## Header
<h1>Class ${unit.name}</h1>
<div id="path">${link_to_unit(unit)}</div>

<p>${unit.docline}</p>

## Declaration
<h2>Declaration</h2>
<div class="decl">
%if unit.decorators:
    <i>
    % for decorator in unit.decorators:
    @${decorator}<br/>
    % endfor
    </i>
%endif
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

<%
  functions = unit.functions(public=True)
  instance_methods = [u for u in functions if not u.is_static()]
  class_methods = [u for u in functions if u.is_static()]
%>

## Instance methods
% if instance_methods:
<h2>Methods</h2>
<ul class="deflst">
% for child in instance_methods:
    <li>
        ${function_desc(child)}
    </li>
% endfor
</ul>
% endif

## Static methods
% if class_methods:
<h2>Class methods</h2>
<ul class="deflst">
% for child in class_methods:
    <li>
        ${function_desc(child)}
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

## -- Subclasses
% if unit.subclasses:
<h2>Subclasses</h2>
<ul class="deflst">
% for u in unit.subclasses:
    <li>${link_to_unit(u)}</li>
% endfor
</ul>
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
