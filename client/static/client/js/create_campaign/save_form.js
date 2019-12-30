if (typeof DEBUG === 'undefined')
  var DEBUG = true;  // false

// global form variable
$(function () {

  $(document).on('change', '.save_data', function (e) {
    DEBUG && console.log("Change event of input with class save_data occurred : ", this)
    save_form_data(this);
  });

});

function save_form_data(ele_input) {
  var campaign_id = $("input[name=campaign]").first().val();
  var url = "";
  if ((campaign_id === "") || (campaign_id === null) || (campaign_id === undefined)) {
    DEBUG && console.log("campaign element i.e. campaign_id  is either empty or undefined so skipping ajax request to save data");
    $.confirm({
      title: 'Encountered an error!',
      content: 'campaign element i.e. campaign_id  is either empty or undefined so skipping ajax request to save data',
      type: 'red',
      typeAnimated: true,
    });
    return false;
  }
  else {
    url = $(ele_input).closest(".form-group").find(".url_holder_save_data").val();
    DEBUG && console.log("url_to_save_data : ", url);

    var ele_form_save_data = $("#form_save_campaign_data").get();
    DEBUG && console.log("Form element to save data : ", ele_form_save_data);

    var new_fields_holder = $(ele_form_save_data).find(".new_fields_holder").get();
    DEBUG && console.log(" New Field holder div of form : ", new_fields_holder);

    // append current input element to form
    // $(new_fields_holder).append(ele_input);
    // DEBUG && console.log("Element input appended to 'form new field holder' div");

    var field_name = $(ele_input).attr("name");
    DEBUG && console.log("Field name : ", field_name);
    var field_value = $(ele_input).val();
    DEBUG && console.log("Field Value : ", field_value);

    $(new_fields_holder).append(
      $('<input>', {
        type: 'text',
        name: 'field_name',
        val: field_name,
      })
    );

    $(new_fields_holder).append(
      $('<input>', {
        type: 'text',
        name: 'field_value',
        val: field_value,
      })
    );

    var serialized_data = $(ele_form_save_data).serializeArray();
    console.log(" serialized_data : ", serialized_data);

    // remove current input element from form // make empty
    $(new_fields_holder).html('');
    DEBUG && console.log("Element input removed from 'new field holder' inside form after serializing data");

    // make ajax call and save data
    $.ajax({
      context: document.body, // access form inside
      url: url, //'/ajax/validate_username/',
      type: "POST",
      data: serialized_data,
      dataType: 'json',
      success: function (response) {
        //console.log(document.body); //current form passed by context
        console.log('Ajax response : ' + JSON.stringify(response))

        if (response.success) {

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
        handle_ajax_error(jqXHR, exception);
      },
    })
  }
}

var check_connectivity = {
  is_internet_connected: function () {
    return $.get({
      url: "https://www.google.com/",
      dataType: 'text',
      cache: false
    });
  }
};

function handle_ajax_error(jqXHR, exception) {
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
}

function show_notification(message) {
  message.type = message.title || 'error'; // store it in type if not null before modification
  message.title = message.title || 'error';
  message.title = message.title.charAt(0).toUpperCase() + message.title.substr(1); //uppercase first char
  message.message = message.message || 'Error while connecting Server';

  new PNotify({
    title: message.title,//'success',
    text: message.message,
    //addclass: 'alert alert-success alert-styled-left alert-arrow-left',
    addclass: 'alert alert-' + message.type + ' alert-styled-left alert-arrow-left',
    type: message.type,//'success',
    delay: 6500  // 3.5 seconds
  });
}
