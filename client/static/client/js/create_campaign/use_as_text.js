if(typeof DEBUG === 'undefined')
      var DEBUG =  true;  // false

$(document).ready(function(){
   // on ready
   // iterate inside checkbox_container div classes if one of use as textbox is shown then remove hidden from
   // all textbox of checkbox_container div // and make use as textbox checked
   $("body").find(".checkbox_container").each(function(){
     is_txtbx_use_as_txt_visible = false;
     // iterate inside all txtbx_use_as_txt
     $(this).find(".txtbx_use_as_txt").each(function(){
        // textbox
        // if hidden class not available
        if(!$(this).hasClass("hidden"))
        {
          is_txtbx_use_as_txt_visible = true;
        }
     });

     if(is_txtbx_use_as_txt_visible)
     {
       // make all textboxes visible
       $(this).find(".txtbx_use_as_txt").each(function(){
         // textbox
         $(this).removeClass("hidden");
       });

       // make use as text checkbox checked
       $(this).closest(".beefup__body").find(".chkbx_use_as_txt").first().attr('checked', true);
     }

   });

});

$(function(){
  $(document).on('click', '.chkbx_use_as_txt', function(e){
     DEBUG && console.log(".chkbx_use_as_txt clicked");

      // find parent class name in data attribute
      var parent_class_name = $(this).data("parent"); // parent to traverse upto // main container
      DEBUG && console.log("parent_class_name : ", parent_class_name);

      // get parent element dom
      var parent_element = $(this).closest("." + parent_class_name).get();
      DEBUG && console.log("parent_element: ", parent_element);

      var txtbx_use_as_text_class = "." + "txtbx_use_as_txt" ;

     if($(this).is(':checked'))
     {
         // remove hidden class from all txtbx_use_as_txt of parent
         $(parent_element).find(txtbx_use_as_text_class).each( function (){
             $(this).removeClass("hidden");
         });
         DEBUG && console.log("Hidden class remoed from all textboxes(use as text) of parent");

     }
     else
     {
         // add hidden class to use as text
          // remove hidden class from all txtbx_use_as_txt of parent
         $(parent_element).find(txtbx_use_as_text_class).each( function (){
             $(this).addClass("hidden");
         });
         DEBUG && console.log("Hidden class added to all textboxes(use as text) of paarent");

         // also clear mapped text  which is stored inside database using ajax call
     }

  });

  $(document).on('keyup', '.txtbx_use_as_txt', function(e){
     DEBUG && console.log(".txtbx_use_as_txt blured");
     var alternative_txt = $(this).val();
     DEBUG && console.log("alternative_txt  : ", alternative_txt );

     // get sibling input value
      var original_txt = $(this).closest(".row").find("input[type='checkbox']").first().data("txt");
      DEBUG && console.log("original_txt from closest '.row' selector: ", original_txt );

      if (original_txt == undefined)
      {
        var original_txt = $(this).closest("tr").find("input[type='checkbox']").first().data("txt");
        DEBUG && console.log("original_txt from closest '.radio class' : ", original_txt );
      }
      var length_alternative_txt = alternative_txt.length
      DEBUG && console.log("Length of alternative_txt  : ", length_alternative_txt );

      /*
       * last time saved value in database
        * used in two cases
        * 1 ) If current value is null and last time  saved value is not empty then it means it removes alternative text for that field
        * 2) If current value === last saved value then there is no need to update value in database
       */
       var last_saved_value = $(this).data("last_saved_value");
       if(typeof last_saved_value === 'undefined')
       {
          last_saved_value = "";
       }

      //  id_camapaign
      var campaign_id = $("#id_campaign").val();
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

      if(length_alternative_txt && last_saved_value =="")
        DEBUG && console.log("Length of alternative text is less than min length attribute value  and last saved value is empty so skipping fruther process");

      var csrfmiddlewaretoken = $("input[name='csrfmiddlewaretoken']").val();
                            DEBUG && console.log(" csrfmiddlewaretoken : ", csrfmiddlewaretoken);
     

      if((length_alternative_txt > 0) )
      {
          // if length of alternative text is zero then delete else update
          // make ajax call
          var data = {
               campaign_id : campaign_id,
               original_txt : original_txt,
               alternative_txt : alternative_txt,
              csrfmiddlewaretoken : csrfmiddlewaretoken,
          }
          DEBUG && console.log("Data while saving use as txt :", data)
          checkpattern(this,alternative_txt)
            save_alternative_text(this, data);
      }

  });

  function checkpattern(element,obj) {
    if (obj != '') {

    
    if ($(element).closest('.card').data('invoke-div') == "revenue_size"){
      if (/^[{m,i,l,o,n,b} 0-9\$\-\.\s]*$/i.test(obj)){
        $(element).css('border', '1px solid green')
        return true
      }else {
        $(element).css('border', '1px solid red')
      }
    } else if($(element).closest('.card').data('invoke-div') == "company_size"){
      if (/^[0-9\-\s]*$/i.test(obj)){
        $(element).css('border', '1px solid green')
        return true
      }else {
        $(element).css('border', '1px solid red')
      }
    } else if (/^[a-zA-Z][a-zA-Z\s]*$/i.test(obj)){
        $(element).css('border', '1px solid green')
        return true
    } else {
      $(element).css('border', '1px solid red')

    }
  } else {
    $(element).css('border','')
  }
    // return alert(false)
};

  $(document).on('blur', '.txtbx_use_as_lead_limit', function(e){
    
    DEBUG && console.log(".txtbx_use_as_lead_limit blured");
    var lead_limit = $(this).val();
    DEBUG && console.log("lead_limit  : ", lead_limit );

  
     //  id_camapaign
     var campaign_id = $("#id_campaign").val();
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

     var csrfmiddlewaretoken = $("input[name='csrfmiddlewaretoken']").val();
                          

     if((lead_limit >=0) )
     {
         // if length of alternative text is zero then delete else update
         // make ajax call
         var data = {
              campaign_id : campaign_id,
              lead_limit : lead_limit,
             csrfmiddlewaretoken : csrfmiddlewaretoken,
         }
         DEBUG && console.log("Data while saving use as txt :", data)
         save_lead_limit(this, data);
     }

  });

});
function save_lead_limit(current_element,data){
  
  var url = $("#link_save_lead_limitation").val();
  if(url)
  {
    DEBUG && console.log('Making ajax request');

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

function save_alternative_text(current_element, data)
{
     var url = $("#link_save_text_mapping").val();
     if(url)
     {
       DEBUG && console.log('Making ajax request');

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


// saving delevery methods comments
$(document).on('blur', '.comment_box', function(e){

  $.ajax({
    context: document.body, // access form inside
    url: '/client/save_delivery_method_comments/',
    type: "POST",
    data: {'element':$(this).attr('data-value'),'data':$(this).val(),'campaign_id':$("#id_campaign").val() },
    dataType: 'json',
    success: function (response) {
      DEBUG && console.log('response : ' + JSON.stringify(response));
      //show_notification(response);
      if(response.success)
      {

      }
    },// success end
  })
})