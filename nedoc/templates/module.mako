<%inherit file="base.mako" />
<%namespace file="utils.mako" import="symbol_link, link_to_source, link_to_unit"/>

## Header
<h1>Module ${link_to_unit(unit)}</h1>

<p>${unit.docline}</p>

${link_to_source(unit)}

## Submodules
% if unit.modules(public=True):
<h2>Submodules</h2>
<ul class="deflst">
% for child in unit.modules(public=True):
    <li><div class="def">Module <a class="symbol" href="${ctx.link_to(child)}">${child.fullname}</a></div>
        % if child.docline:
        <div class="docline">${child.docline}</div>
        % endif
    </li>
% endfor
</ul>
% endif

## Imported Submodules
<% modules = unit.imported_modules(gctx, public=True, export=True) %>
%if modules:
<h2>Re-exported Submodules</h2>
<ul class="deflst">
% for name, child in modules:
    <li><div class="def">Module <a class="symbol" href="${ctx.link_to(child)}">${name}</a></div>
        % if child.docline:
        <div class="docline">${child.docline}</div>
        % endif
        <div class="import"> [${child.fullname}]</div>
    </li>
% endfor
</ul>
% endif


## Classes
% if unit.classes(public=True):
<h2>Classes</h2>
<ul class="deflst">
% for c in unit.classes(public=True):
    <li><div><span class="def">class <a class="symbol" href="${ctx.link_to(c)}">${c.name}</a></span>
    </div>\
    % if c.docline:
        <div class="docline">${c.docline}</div>\
    % endif
    </li>
% endfor
</ul>
% endif


## Imported classes
<% classes = unit.imported_classes(gctx, public=True, export=True) %>
% if classes:
<h2>Re-exported Classes</h2>
<ul class="deflst">
% for name, c in classes:
    <li><div><span class="def">class <a class="symbol" href="${ctx.link_to(c)}">${name}</a></span>
    </div>\
    % if c.docline:
        <div class="docline">${c.docline}</div>\
    % endif
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
    <li><div><span class="def">def <a class="symbol" href="${ctx.link_to(u)}">${u.name}</a>(<span class="args">${u.render_args()}</span>)</span></div>
    % if u.docline:
        <div class="docline">${u.docline}</div>
    % endif
    </li>
% endfor
</ul>
% endif

## Imported Functions
<% functions = unit.imported_functions(gctx, public=True, export=True) %>
% if functions:
<h2>Re-exported Functions</h2>
<ul class="deflst">
% for name, u in functions:
    <li><div><span class="def">def <a class="symbol" href="${ctx.link_to(u)}">${name}</a>(<span class="args">${u.render_args()}</span>)</span></div>
    % if u.docline:
        <div class="docline">${u.docline}</div>
    % endif
        <div class="import"> [${u.fullname}]</div>
    </li>
% endfor
</ul>
% endif

## Documentation
% if unit.docstring:
<h2>Documentation</h2>
${ctx.render_docstring(unit) | n}
% endif