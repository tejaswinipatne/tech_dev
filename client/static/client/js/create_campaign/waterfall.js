if(typeof DEBUG === 'undefined')
      var DEBUG =  true;  // false

$(function(){

  // on blur of cpl and volume textbox
  $(document).on('blur', '.txtbx_volume, .txtbx_cpl', function(e){
    var name = $(this).attr("name");
    DEBUG && console.log(name + " blurred");

    var level_of_intent = $(this).closest("tr").find('.chkbx_level_of_intent').first().data("txt");
    DEBUG && console.log("level_of_intent  : ", level_of_intent);
    
    var volume = $(this).closest("tr").find('.txtbx_volume').first().val();
    DEBUG && console.log("volume  : ", volume);

    var cpl = $(this).closest("tr").find('.txtbx_cpl').first().val();
    DEBUG && console.log("CPL  : ", cpl);

    var campaign_id = get_campaign_id(this);

    if(campaign_id && volume && cpl)
    {
        var csrfmiddlewaretoken = $("input[name='csrfmiddlewaretoken']").val();
        DEBUG && console.log(" csrfmiddlewaretoken : ", csrfmiddlewaretoken);
        var data = {
             campaign_id : campaign_id,
             csrfmiddlewaretoken : csrfmiddlewaretoken,
             level_of_intent : level_of_intent,
             volume : volume,
             cpl : cpl,
        }
        DEBUG && console.log("Data passing to ajax : ", data);
        
        save_volume_and_CPL(this, data);

    }
  });

  // on keyup check remaining volume
  $(document).on('keyup', '.txtbx_volume', function(e){

    var is_checked_level_of_intent = $(this).closest("tr").find('.chkbx_level_of_intent').first().is(':checked');
    DEBUG && console.log(" is_checked_level_of_intent : ", is_checked_level_of_intent);

    if(is_checked_level_of_intent == false)
    {
      /*
      // display notification
    	new PNotify({
    			title: "Error",//'success',
    			text: "Please check Level of intent checkbox First",
    			//addclass: 'alert alert-success alert-styled-left alert-arrow-left',
    			addclass: 'alert alert-error alert-styled-left alert-arrow-left',
    			type: 'error',//'success',
    			delay: 3500  // 3.5 seconds
    	});

      //clear textbox values
      $(this).closest("tr").find('.txtbx_volume').val("");
      $(this).closest("tr").find('.txtbx_cpl').val("");
      
      */
    }

  });

});

function get_campaign_id(current_element)
{
  // get campaign id stored inside form first input //  id_camapaign
  var campaign_id = $("#id_camapaign").val();
  if(typeof campaign_id === 'undefined')
  {
    DEBUG && console.log("campaign_id is undefined");
    campaign_id = "";
  }
  else if(campaign_id == "")
  {
      DEBUG && console.log("campaign_id is empty so skipping fruther process");
  }
  else
  {
      DEBUG && console.log("campaign_id : ", campaign_id);
      campaign_id  = parseInt(campaign_id);
  }
  return campaign_id;
}

function save_volume_and_CPL(current_element, data)
{
     var url = $("#link_save_volume_and_cpl").val();
     if(url)
     {
       DEBUG && console.log('Making ajax request to save volume and CPL');

       $.ajax({
          context: document.body, // access form inside
          url: url, //'/ajax/validate_username/',
          type: "POST",
          data: data,
          dataType: 'json',
          success: function (response) {
            DEBUG && console.log('response : ' + JSON.stringify(response));
            //show_notification(response);
            if(response.success)
            {

            }
          },// success end
       })
    }
    else
    {
      DEBUG && console.log("Url undefined when trying to save text mapping");
    }
}

function delete_volume_and_CPL(current_element, data)
{
     var url = $("#link_delete_volume_and_cpl").val();
     if(url)
     {
       DEBUG && console.log('Making ajax request to delete volume and CPL');

       $.ajax({
          context: document.body, // access form inside
          url: url, //'/ajax/validate_username/',
          type: "POST",
          data: data,
          dataType: 'json',
          success: function (response) {
            DEBUG && console.log('response : ' + JSON.stringify(response));
            //show_notification(response);

          },// success end
       })
    }
    else
    {
      DEBUG && console.log("Url undefined when trying to delete cpl and volume");
    }
}
