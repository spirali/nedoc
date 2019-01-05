$(function() {
    var NEDOC_MODULES = JSON.parse('%MODULES%');
    $("#search").autocomplete({
    source: NEDOC_MODULES.map(function(i) { return { label: i[0], desc: i[1], fulllink: i[2] }; }),
    select: function(event, ui) {
        if (ui.fulllink) {
            window.location.href = ui.item.desc + "." + ui.item.label + ".html";
        } else {
            window.location.href = ui.item.desc + ".html#" + ui.item.label;
        }
    },
    }).autocomplete("instance")._renderItem = function(ul, item) {
        return $("<li>")
            .append("<div><b>" + item.label + "</b><br>" + item.desc + "</div>")
            .appendTo(ul);
    };

    $(".fexpand").on("click", function(event) {
        event.preventDefault();
        var elem = $(this);
        var parent = elem.closest(".fn");
        parent.children(".fdetail").toggle(200);
    })

    if(window.location.hash) {
        var name = window.location.hash.slice(3); // remove #f_ prefix
        var elem = $("#fn_" + name);
        elem.toggle(0);
        elem.parent().parent().css("backgroundColor", "#e9f6ff");
    }
});
