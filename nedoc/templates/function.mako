<%namespace file="utils.mako" import="link_to_unit, link_to_source, symbol_link"/>
<%namespace file="docstring.mako" import="render_docstring, render_docline"/>
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
    <div class="fn"><a id="f_${unit.name}"></a>
        <div class="fshort">
        <%
           limit = 80
           if unit.returns:
                limit -= len(unit.returns) + 4
           long_args, rargs = unit.render_args(limit=limit)
           has_more = long_args | bool(unit.overriden_by) | bool(unit.aliases) | bool(unit.overrides)
           if not has_more:
                pd = ctx.get_parsed_docstring(unit)
                has_more = pd.has_more()
        %>
        <span class="def"><span class="ftoggle${"" if has_more else "-empty"}">${"&#9654;" if has_more else "&#9655;" | n}</span> def <a class="fexpand symbol${"" if unit.docstring else "-no-doc"}" href="${ctx.link_to(unit)}">${unit.name}</a>(<span class="args">${rargs}</span>)${" -> " + unit.returns if unit.returns else ""}
        ${function_labels(unit)}
        </span>
        ${render_docline(ctx, unit, True)}
        </div>
        <div class="fdetail" id="fn_${unit.name}">
            ${function_detail(unit, long_args)}
        </div>
    </div>
</%def>

<%def name="function_detail(unit, long_args)">
    <% arg_style = {
        "self_style": ("<span class='kw'>", "</span>"),
        "default_style": ("<i>", "</i>")
    }
    %>

    % if long_args or unit.decorators:
        <div class="decl">
            <div class="def">
            %if unit.decorators:
                <i>
                % for decorator in unit.decorators:
                @${decorator}<br/>
                % endfor
                </i>
            %endif
            %if len(unit.args) + len(unit.kwonlyargs) <= 1:
                <span class="kw">def</span> ${unit.name}(<span class="args">${unit.render_args(limit=None, **arg_style) | n}</span>)
            %else:
                <span class="kw">def</span> ${unit.name}(
                % for arg in unit.args:
                <div class="args" style="padding-left: 2em">${arg.render(**arg_style) | n},</div>
                % endfor
                % if unit.vararg:
                <div class="args" style="padding-left: 2em">*${unit.vararg},</div>
                % elif unit.kwonlyargs:
                <div class="args" style="padding-left: 2em">*,</div>
                % endif
                % for arg in unit.kwonlyargs:
                <div class="args" style="padding-left: 2em">${arg.render(**arg_style) | n},</div>
                % endfor
                % if unit.kwarg:
                <div class="args" style="padding-left: 2em">**${unit.kwarg},</div>
                %endif
                )${" -> " + unit.returns if unit.returns else ""}
            %endif
            </div>
        </div>
    % endif

    <div class="idnt">${link_to_source(unit)}</div>

    % if unit.overrides:
    <p>This method overrides ${link_to_unit(unit.overrides)}.</p>
    % endif

    ## -- Documentation
    ${render_docstring(ctx, unit)}

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