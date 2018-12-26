<%namespace file="utils.mako" import="link_to_unit, link_to_source, symbol_link"/>
<%inherit file="base.mako" />

<%def name="function_labels(unit)">\
% if unit.overrides:
<span class="label">override</span> \
% endif
% if len(unit.decorators) < 3:
    % for decorator in unit.decorators:
    <span class="label">@${decorator}</span> \
    %endfor
% else:
    <span class="label">${len(unit.decorators)} decorators</span> \
% endif
</%def>

<%def name="function_desc(unit)">
    <div class="fn"><a id="${unit.name}"></a>
        <div class="fshort">
        <span class="def">def <a class="fexpand symbol" href="${ctx.link_to(unit)}">${unit.name}</a>(<span class="args">${unit.render_args()}</span>)
        ${function_labels(unit)}
        </span>
        % if unit.docline:
            <div class="docline">${unit.docline}</div>
        % else:
            <% docline = unit.overriden_docline() %>
            % if docline:
                <div class="docline"><span class="label">inherited doc</span> ${docline}</div>
            %endif
        % endif
        </div>
        <div class="fdetail" id="fn_${unit.name}">
            ${function_detail(unit)}
        </div>
    </div>
</%def>

<%def name="function_detail(unit)">
    <% arg_style = {
        "self_style": ("<span class='kw'>", "</span>"),
        "default_style": ("<i>", "</i>")
    }
    %>
    <h3>Declaration</h3>
    <div class="decl">
    <div class="def">
    %if unit.decorators:
        <i>
        % for decorator in unit.decorators:
        @${decorator}<br/>
        % endfor
        </i>
    %endif
    %if len(unit.args) <= 1:
        <span class="kw">def</span> ${unit.name}(<span class="args">${unit.render_args(**arg_style) | n}</span>):
            <div class="idnt">${link_to_source(unit, "source code")}</div>
    %else:
        <span class="kw">def</span> ${unit.name}(
        % for arg in unit.args:
        <div class="args" style="padding-left: 2em">${arg.render(**arg_style) | n}${"," if not loop.last else ""}</div>
        % endfor
        ):
        <div class="idnt">${link_to_source(unit, "source code")}</div>
    %endif
    </div>
    </div>

    % if unit.overrides:
    <p>This method overrides ${link_to_unit(unit.overrides)}.</p>
    % endif

    ## -- Documentation
    % if unit.docstring:
        <h3>Documentation</h3>
        ${ctx.render_docstring(unit) | n}
    % elif unit.overriden_docstring():
        <h3>Documentation</h3>
        <span class="label">inherited documentation</span>
        ${ctx.render_docstring(unit.overriden_docstring()) | n}
    %endif

    ## -- Overrides
    % if unit.overriden_by:
    <h3>Overrides</h3>
        <p>This method is overriden in:</p>
        <ul class="deflst2">
        % for u in unit.overriden_by:
            <li>${link_to_unit(u.parent)}</li>
        % endfor
        </ul>
    % endif

    ## Aliases
    %if unit.aliases:
        <h3>Reexports</h3>
        <ul class="deflst2">
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
</%def>