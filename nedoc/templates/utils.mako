<%def name="symbol_link(cname, abolute=False)">\
<% href=ctx.link_to_cname(cname, abolute) %>\
% if href:
<a class="symbol" href="${href}">${render_cname(cname)}</a>\
% else:
${render_cname(cname)}\
% endif
</%def>

<%def name="link_to_source(unit, label='Source code')">\
% if ctx.link_to_source(unit.module()):
<a class="sourcelink" href="${ctx.link_to_source(unit.module())}">${label}</a>\
% endif
</%def>

<%def name="link_to_unit(unit, last_name_only=False)">\
% if last_name_only:
<a class="symbol" href="${ctx.link_to(unit)}">${unit.name}</a>\
% else:
% for m in unit.path:
<a class="symbol" href=${ctx.link_to(m)}>${m.name}</a>${'' if loop.last else '.'}\
%endfor
% endif
</%def>