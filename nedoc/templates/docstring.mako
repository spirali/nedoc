
<%def name="render_docline(ctx, unit, include_more_symbol=False)">
    <%
        pd = ctx.get_parsed_docstring(unit)
    %>
    % if pd.docline:
        <div class="docline">
        % if not unit.has_own_docstring:
        <span class="label">inherited doc</span>
        % endif
        ${pd.docline}
        </div>
    % endif
</%def>

<%def name="render_docstring(ctx, unit)">
    <% pd = ctx.get_parsed_docstring(unit) %>
    % if pd.description:
        ${render_paragraph(ctx, pd.description)}
    %endif

    % if unit.role == "function":
        % if pd.params:
        <h3>Parameters</h3>
        ${render_list(ctx, pd.params)}
        % endif

        % if pd.returns:
        <h3>Returns</h3>
        ${render_list(ctx, pd.returns)}
        % endif

        % if pd.raises:
        <h3>Raises</h3>
        ${render_list(ctx, pd.raises)}
        % endif
    % endif

    % if pd.subsections:
    % for (name, text) in pd.subsections:
    <h3>${name}</h3>
    ${render_paragraph(ctx, text)}
    % endfor
    % endif
</%def>


<%def name="render_list(ctx, lst)">
    <% if not isinstance(lst, (list, tuple)):
           lst = [lst]
    %>
    <ul class="params">
    % for item in lst:
    ${render_item(ctx, item)}
    % endfor
    </ul>
</%def>

<%def name="render_item(ctx, item)">
    <li>
    % if hasattr(item, "arg_name") and hasattr(item, "type_name"):
        <strong>${item.arg_name}</strong>: ${item.type_name}
    % elif hasattr(item, "arg_name"):
        <strong>${item}.arg_name}</strong>
    % elif hasattr(item, "type_name"):
        ${item.type_name}
    %endif
    % if item.description:
        <br/>${render_paragraph(ctx, item.description)}
    %endif
    </li>
</%def>

<%def name="render_paragraph(ctx, text)">
    ${ctx.render_paragraph(text) | n}
</%def>