<%inherit file="base.mako" />

<h1>Source code ${unit.source_filename}</h1>

${ctx.format_code(unit.source_code) | n}
