$(document).ready(function() {
    var existing_exp = $("#existing_experience");
    var new_exp = $("#new_experience");
    existing_exp.prop("value", "");
    new_exp.prop("checked", false);

    existing_exp.change(function() {
        if ($(this).val() && new_exp.is(":checked")) {
            new_exp.prop("checked", false);
            toggle_div("new_experience_form");
        }
    })

    new_exp.change(function() {
        if ($(this).is(":checked")) {
            existing_exp.prop("value", "");
        }
    })
})
