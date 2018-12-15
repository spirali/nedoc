$(function() {
    var NEDOC_MODULES = JSON.parse('%MODULES%');
    $("#search").autocomplete({
    source: NEDOC_MODULES.map(function(i) { return { label: i[0], desc: i[1] }; }),
    select: function(event, ui) {
        window.location.href = ui.item.desc + "." + ui.item.label + ".html";
    },
    }).autocomplete("instance")._renderItem = function(ul, item) {
        return $("<li>")
            .append("<div><b>" + item.label + "</b><br>" + item.desc + "</div>")
            .appendTo(ul);
    };
});
