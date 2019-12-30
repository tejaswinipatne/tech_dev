if(typeof DEBUG === 'undefined')
      var DEBUG =  true;  // false

$(function(){

  // on click of change campaign status button
  // check is mandatory fields are checked
  $(document).on('click', '#btn_change_campaign_status', function(e){

    var res = false; // to stop bulk errors ckheck is function returns true
    
    res  = header_check()
    // check is industry type selected
    res = validate_element_value({
      field_name:'industry_type',
      error_msg: "Please Select Industry Type ",
    })


    
    // to stop bulk errors ckheck is function returns true
    // check is Job level selected
    if(res)
    {
      res = validate_element_value({
        field_name:'job_level',
        error_msg: "Please Select Job Level",
      })
    }

    // check is Country selected
    if(res)
    {
      res = validate_element_value({
        field_name:'country',
        error_msg: "Please Select Country",
      })
    }

    // check is Company Size selected
    if(res)
    {
      res = validate_element_value({
        field_name:'company_size',
        error_msg: "Please Select Employee Size",
      })
    }

    // check is Data Fields selected
    // if(res)
    // {
    //   res = validate_element_value({
    //     field_name:'data_header',
    //     error_msg: "Please Select Data Fields",
    //   })
    // }
    

    // trigger change status link click
    if(res)
    {
      DEBUG && console.log("setting window.location to href of link_change_campaign_status")
      window.location = $("#link_change_campaign_status").attr('href');
    }
    else
    {
      DEBUG && console.log("Problem while triggering link_change_campaign_status click")
    }
  });

});


function validate_element_value(options) 
{
  var defaults = {
    field_name:'industry_type',
    err_title: "Encountered an error !",
    error_msg: "Please select field",
    msg_type: "red",
  };

  var params = $.extend({}, defaults, options);

  // console.log(options);
  // console.log(params);

  var value = $("input[name='"+ params.field_name +"']").val();
  DEBUG && console.log("Element with name :'", params.field_name, "' has value : ", value);

  if(value !== 'undefined')
  {
    if(value == "" || value == null || value =="['None']" || value=="None")
    {
      $.confirm({
        title: params.err_title,
        content: params.error_msg,
        type: params.msg_type,
      });
      return false;
    }
    else
    {
      DEBUG && console.log("Value of input textbox element with name '" + params.field_name + "' looks ok"); 
      return true;
    }
  }
  else
  {
    DEBUG && console.log("Problem while fetching "+ params.field_name +" input textbox element"); 
    return false;
  }

  return false
}


function header_check(){
  tc_header = $('#id_tc_header_status').is(':checked')
  custom_header = $('#id_custom_header_status').is(':checked')
  if (tc_header == false && custom_header == false){
    $.confirm({
      title:  "Encountered an error !",
      content:  "Please Select Data Fields !",
      type: "red",
    });
    return false;
  }
  if (tc_header == true){
    if ($('.tc_header_div').find('input[type="checkbox"]:checked').length == 0){
      $.confirm({
        title:  "Encountered an error !",
        content:  "Please Select Data Fields !",
        type: "red",
      });
      return false;
    }
  }
  return true;
}