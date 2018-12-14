<%inherit file="base.mako" />
<%namespace file="utils.mako" import="link_to_unit"/>

<h1>Source code ${unit.source_filename}</h1>
<div id="path">${link_to_unit(unit)}</div>

${ctx.format_code(unit.source_code) | n}
