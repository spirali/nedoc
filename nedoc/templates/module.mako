<%inherit file="base.mako" />
<%namespace file="utils.mako" import="symbol_link, link_to_source, link_to_unit"/>
<%namespace file="function.mako" import="function_desc"/>
<%namespace file="docstring.mako" import="render_docstring, render_docline"/>

## Header
<h1>Module ${unit.name}</h1>
<div id="path">${link_to_unit(unit)}</div>

% if unit.docstring:
${render_docline(ctx, unit)}
${render_docstring(ctx, unit)}
% endif

${link_to_source(unit)}

## Classes
% if unit.classes(public=True):
<h2>Classes</h2>
<ul class="deflst">
% for c in unit.classes(public=True):
    <li>\
    <div>\
        <span class="def">class <a class="symbol" href="${ctx.link_to(c)}">${c.name}</a></span>\
    </div>\
    ${render_docline(ctx, c)}
    </li>
% endfor
</ul>
% endif


## Imported classes
<% classes = sorted(unit.imported_classes(gctx, public=True, export=True)) %>
% if classes:
<h2>Re-exported Classes</h2>
<ul class="deflst">
% for name, c in classes:
    <li>\
    <div>\
        <span class="def">class <a class="symbol" href="${ctx.link_to(c)}">${name}</a></span>\
    </div>\
    ${render_docline(ctx, c)}
    <div class="import"> [${c.fullname}]</div>\
    </li>
% endfor
</ul>
% endif


## Functions
% if unit.functions(public=True):
<h2>Functions</h2>
<ul class="deflst">
% for u in unit.functions(public=True):
    <li>
        ${function_desc(u)}
    </li>
% endfor
</ul>
% endif

## Imported Functions
<% functions = sorted(unit.imported_functions(gctx, public=True, export=True)) %>
% if functions:
<h2>Re-exported Functions</h2>
<ul class="deflst">
% for name, u in functions:
    <li><div><span class="def">def <a class="symbol" href="${ctx.link_to(u)}">${name}</a>(<span class="args">${u.render_args()}</span>)</span></div>
    ${render_docline(ctx, u)}
    <div class="import"> [${u.fullname}]</div>
    </li>
% endfor
</ul>
% endif

## Submodules
% if unit.modules(public=True):
<h2>Submodules</h2>
<ul class="deflst">
% for child in unit.modules(public=True):
    <li><div class="def">Module <a class="symbol" href="${ctx.link_to(child)}">${child.fullname}</a></div>
    ${render_docline(ctx, child)}
    </li>
% endfor
</ul>
% endif

## Imported Submodules
<% modules = sorted(unit.imported_modules(gctx, public=True, export=True)) %>
%if modules:
<h2>Re-exported Submodules</h2>
<ul class="deflst">
% for name, child in modules:
    <li><div class="def">Module <a class="symbol" href="${ctx.link_to(child)}">${name}</a></div>
        ${render_docline(ctx, child)}
        <div class="import"> [${child.fullname}]</div>
    </li>
% endfor
</ul>
% endif
