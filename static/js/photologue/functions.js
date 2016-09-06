$(document).ready(function() {
    var options = {
        //target:   '#photo_form_feedback',   // target element(s) to be updated with server response
        // beforeSubmit:  beforeSubmit,  // pre-submit callback
        resetForm: true, // reset the form after successful submit
        error: somethingWrong,
        dataType: 'json',
        success: show_photo,
    };
       
    $('#photo_form').submit(function() {
        $("#ajax-loader").toggle();
        $(this).ajaxSubmit(options);
        // return false to prevent standard browser submit and page navigation
        return false;
    });

    function show_photo(r){
        $("#ajax-loader").toggle();
        $("<div class=\"cell\"><div class=\"photo_item\">" + r.html + "</div></div>").hide().prependTo(".thirds_table").fadeIn("slow");
        $("#no-photos").remove();
    }

    function somethingWrong(jqXHR, textStatus, errorThrown){
        alert("Sorry, there was an error");
        $("#ajax-loader").toggle();
    }
})
