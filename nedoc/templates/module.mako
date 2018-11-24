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

## Classes
% if unit.all_classes(gctx, public=True):
<h2>Classes</h2>

<ul class="deflst">
% for uc in unit.all_classes(gctx, public=True):
    <li><div> <span class="def">class <a class="symbol" href="${ctx.link_to(uc.unit)}">${uc.name}</a></span>
        % if uc.imported:
        <div class="import"> [imported ${uc.unit.fullname}]</div>\
        % endif
        </div>\
        % if uc.unit.docline:
        <div class="docline">${uc.unit.docline}</div>\
        % endif
    </li>
% endfor
</ul>
% endif


## Functions
% if unit.all_functions(gctx, public=True):
<h2>Functions</h2>
<ul class="deflst">
% for uc in unit.all_functions(gctx, public=True):
    <li><div><span class="def">def <a class="symbol" href="${ctx.link_to(uc.unit)}">${uc.name}</a>(<span class="args">${uc.unit.render_args()}</span>)</span>
        % if uc.imported:
        <div class="import"> [imported ${uc.unit.fullname}]</div>
        % endif
        </div>
        % if uc.unit.docline:
        <div class="docline">${uc.unit.docline}</div></li>
        % endif
% endfor
</ul>
% endif


## Documentation
% if unit.docstring:
<h2>Documentation</h2>
${ctx.render_docstring(unit) | n}
% endif