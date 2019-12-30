if (typeof DEBUG === 'undefined')
    var DEBUG = true;  // false


$(document).ready(function () {
    // on ready
    // ierate inside all card and check is data-is_user_set_default="True"
    $("body").find("#board3").find(".card").each(function () {

        var $is_user_set_default = $(this).data("is-user-set-default");
        DEBUG && console.log("$is_user_set_default : ", $is_user_set_default);

        if ($is_user_set_default == "True") {
            // check the  set as default checkbox
            $chk_bx_set_default = $(this).find(".chk_bx_set_default").get();
            DEBUG && console.log("$chk_bx_set_default : ", $chk_bx_set_default);

            if ($chk_bx_set_default) {
                $($chk_bx_set_default).attr('checked', true);
                DEBUG && console.log("Making above checkbox checked");
            }

        }

    });

});

$(function () {

    // onclick of sel default checkbox set this field as default selected 
    $(document).on("click", ".chk_bx_set_default", function () {

        DEBUG && console.log(".chk_bx_set_default clicked ");

        // using var chaining
        var
            $card = $(this).closest(".card"),
            $invoke_div_name = $card.data("invoke-div"),

            $beefup_body = $(this).closest(".beefup__body"),
            //$card_name = $.data($card, "invoke-div"), // faster than $('#id').data()
            $checkbox_container = $beefup_body.find(".checkbox_container"),
            $ele_input = $checkbox_container.find(".save_data").first(),
            $value = $ele_input.val();

        DEBUG && console.log("$invoke_div_name : '" + $invoke_div_name + "'");
        DEBUG && console.log("$value of hidden input: '" + $value + "'");

        if ($invoke_div_name && $value) {
            var $arr_invalid_vals = [
                "None",
                "['None']",
                "'None'"
            ];

            if ($.inArray($value, $arr_invalid_vals) != -1) {
                // found it
                DEBUG && console.log("value of $value looks invalid because value exists in $arr_invalid_vals ")
            }
            else {
                var $data = {
                    invoke_div_name: $invoke_div_name,
                    value: $value,
                    csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").first().val(),
                }

                // value is valid process fruther
                var $is_checked = $(this).is(":checked");

                if ($is_checked) {
                    // add data
                    DEBUG && console.log("Checkbox is checked so adding 'set as default' data to table");

                    // get url
                    var $url = $("#link_add_set_as_default").val();
                    if ($url) {

                        ajax_set_as_default($url, $data);
                    }
                    else {
                        DEBUG && console.log("Error while getting 'add set as default' url from element");
                    }
                }
                else {
                    // remove data from table
                    DEBUG && console.log("Checkbox is un-checked so removing 'set as default' data from table")

                    // get url
                    var $url = $("#link_remove_set_as_default").val();
                    if ($url) {

                        ajax_set_as_default($url, $data);
                    }
                    else {
                        DEBUG && console.log("Error while getting 'remove set as default' url from element");
                    }

                }
            }
        }
        else {
            DEBUG && console.log("Problem while fetching either selected value or name of hidden input")
        }
    });
});

function ajax_set_as_default($url, $data) {
    // make ajax call and save data
    $.ajax({
        context: document.body, // access form inside
        url: $url, //'/ajax/validate_username/',
        type: "POST",
        data: $data,
        dataType: 'json',
        success: function (response) {
            console.log('Ajax response (from set as default) : ', response)
            //console.log('Ajax response : ' + JSON.stringify(response))

            //            if(response.success)
            if (response.success) {
                show_notification(response)
            }
            else {
                $.confirm({
                    title: 'Encountered an error!',
                    content: response.message,
                    type: 'red',
                    typeAnimated: true,
                });
            }
        },
        error: function (jqXHR, exception) {
            var msg = '';
            if (jqXHR.status === 0) {
                msg = 'Server Unreachable.\n 1) Verify Network. \n 2) Or Server Down';
            }
            else if (jqXHR.status == 404) {
                msg = 'Requested page not found. [404]';
            }
            else if (jqXHR.status == 500) {
                msg = 'Internal Server Error [500].';
            }
            else if (exception === 'parsererror') {
                msg = 'Requested JSON parse failed.';
            }
            else if (exception === 'timeout') {
                msg = 'Time out error.';
            }
            else if (exception === 'abort') {
                msg = 'Ajax request aborted.';
            }
            else {
                msg = 'Uncaught Error.\n' + jqXHR.responseText;
            }
            DEBUG && console.log(msg);
            $.confirm({
                title: 'Encountered an error!',
                content: msg,
                type: 'red',
                typeAnimated: true,
            });
        },
    })
    return true;
}
