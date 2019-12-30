$(function () {
  $(document).on('change', '.checkbox_container input[type="checkbox"]', function () {
    //$('input[name="' + this.name + '"]').not(this).prop('checked', false);
    var current_checkbox = this;
    var checkbox_name = this.name;
    var selected_values = [];

    // iterate in all chckbox with same name to get clicked values
    $('input[name="' + checkbox_name + '"]').each(function () {
      console.dir("this.value : " + this.value);
      if ($(this).is(':checked')) {
        console.dir("Checked");
        console.dir(this.value);
        selected_values.push(this.value);
        // push values into array
      }
    });
    if ($('input[name="' + checkbox_name + '"]:checked').length == $('input[name="' + checkbox_name + '"]').length){
      $(current_checkbox).parents('article').find('.chk_bx_select_all').prop('checked',true)
    } else{
      $(current_checkbox).parents('article').find('.chk_bx_select_all').prop('checked',false)
    }
    
    // each end
    checked_values_as_str(selected_values, current_checkbox);
  });

  // select
  $(document).on('click', '.chk_bx_select_all', function (e) {
    var selected_values = [];

    if ($(this).is(':checked')) {
      // checking all checkboxes
      // DEBUG && console.log('Selecting all checkboes of current checkbox container');
      $(this).closest(".beefup__body").find(".checkbox_container").find("input[type='checkbox']").prop('checked', true);
    }
    else {
      // deselecing all checkboxes
      // DEBUG && console.log('Removing selection of all checkboes of current checkbox container');
      $(this).closest(".beefup__body").find(".checkbox_container").find("input[type='checkbox']").prop('checked', false);
    }

    // iterate in all chckbox with same name to get clicked values
    $(this).closest(".beefup__body").find(".checkbox_container").find("input[type='checkbox']").each(function () {
      console.dir("this.value : " + this.value);
      if ($(this).is(':checked')) {
        DEBUG && console.dir("Checked");
        DEBUG && console.dir(this.value);
        selected_values.push(this.value);
        // push values into array
      }
    });
    // each end
    checked_values_as_str(selected_values, this);
  });

  // ad-hoc checkbox
  $(document).on('change', '.chk_put_vals', function () {
    //$('input[name="' + this.name + '"]').not(this).prop('checked', false);
    DEBUG && console.log(" chk_put_vals checkbox clicked");

    var value = undefined;
    if ($(this).is(':checked')) {
      DEBUG && console.dir("checkbox is checked");
      value = 1;
    }
    else {
      value = 0;
    }
    var hidden_input = $(this).parent().find('input[type="hidden"]')[0];
    $(hidden_input).val(value);
    DEBUG && console.log("value stored in hidden textbox : ", $(hidden_input).val())

  });
});

function checked_values_as_str(selected_values, current_element) {
  DEBUG && console.dir(selected_values);
  var concatcated_str = selected_values.join();
  DEBUG && console.dir("concatcated_str");
  DEBUG && console.dir(concatcated_str);
  //store it in input hidden element
  var closet_checkbox_container = $(current_element).closest(".beefup__body").find('.checkbox_container');
  //.find('input[type="hidden"]').value=
  DEBUG && console.dir("closet_checkbox_container : ");
  DEBUG && console.dir(closet_checkbox_container);
  var input_element = $(closet_checkbox_container).find('input[type="hidden"]').first();
  DEBUG && console.dir("input_element : ");
  DEBUG && console.dir(input_element);
  //set value
  $(input_element).val(concatcated_str);
  //check inserted value
  DEBUG && console.log(" Input element value : " + $(input_element).val());

  // trigger change event of input element
  $(input_element).trigger("change");
}



$(document).on('change','.lead_choice input[type="checkbox"]',function(){
  console.log($(this))
  campaign_id = $('#id_camapaign').val()
  type = $(this).data('type')
  custom_header = 0
  tc_header = 0
  if (type == 'tc_header_status'){
    if ($(this).is(':checked')){
      tc_header = 1
    } else {
      $('.tc_header_div').find('input[type="checkbox"]').each(function(){
        $(this).prop('checked',false)
        $(this).trigger('change')
      })
    }
  } 
  if (type == 'custom_header_status'){
    if ($(this).is(':checked')){
      custom_header = 1
      campaign_id = $('#id_camapaign').val()
        if(document.getElementById('id_custom_header_status').checked){
            $(".default_header").toggleClass('hidden')
            window.location=`/client/custom-datafields/${campaign_id}`;
            return false;
        }
    } else {
      $('.custom_header_status_container').empty()
      $(".default_header").toggleClass('hidden')
    }
  }
  $.ajax({
    // context: document.body, // access form inside
    url: '/client/save_header_choice/',
    type: "POST",
    data: {'campaign_id':campaign_id,'custom_header':custom_header,'tc_header':tc_header,'type':type},
    dataType: 'json',
    success: function (response) {
      console.log(response)
      location.reload()
      
    },// success end
  })
})