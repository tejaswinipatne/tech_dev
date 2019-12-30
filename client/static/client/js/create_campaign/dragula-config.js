if(typeof DEBUG === 'undefined')
      var DEBUG =  true;  // false

// global
var id_board_drop = "board-drop";
var id_board_drag = "board-drag";
  
var id_component_data_holder = "#component-data-holder";


$(document).ready(function(){

  var containers = [
                    document.querySelector('#'+ id_board_drop), 
                    document.querySelector('#' + id_board_drag),
                   ]
  
  // board 1 
  var drake =  dragula(containers, {
    direction: 'vertical',             // Y axis is considered when determining where an element would be dropped
    copy: false,                       // elements are moved by default, not copied
    copySortSource: false,             // elements in copy-source containers can be reordered
    revertOnSpill: true,              // spilling will put the element back where it was dragged from, if this is true
    removeOnSpill: false,              // spilling will `.remove` the element, if this is true
    mirrorContainer: document.body,    // set the element that gets mirror elements appended
    ignoreInputTextSelection: true,     // allows users to select input text, see details below

    accepts: function (el, target) {
      // if target is drag board dont put element
      return target !== document.getElementById(id_board_drag)
    },
  }).on('drag', function (el) {
      //DEBUG && console.log("Drag event called");
      // Automatically Scroll the page 
      document.onmousemove = (e) => {
        let event = e || window.event;
        let mouseY = event['pageY'];
        let scrollTop = document.documentElement.scrollTop ? document.documentElement.scrollTop : document.body.scrollTop; // document.documentElement.scrollTop is undefined on the Edge browser
        let scrollBottom = scrollTop + window.innerHeight;
        let elementHeight = el.offsetHeight; // this is to get the height of the dragged element

        if (mouseY - elementHeight / 2 < scrollTop) {
            window.scrollBy(0, -15);
        } else if (mouseY + elementHeight > scrollBottom) {
            window.scrollBy(0, 15);
        }
    };
  }).on('dragend', function(el){
    // detach the mouse move event when the drag ends
    document.onmousemove = null;
  }).on('drop', function (el, target, source, sibling) {
      DEBUG && console.log("drop event called ");
      DEBUG && console.log("el : ", el);
      DEBUG && console.log("target : ", target);
      DEBUG && console.log("source : ", source);
      DEBUG && console.log("sibling : ", sibling);

      // call function
      after_element_drop(el, target, source, sibling)

     // var today = new Date();
     // $(el).append("<p>" + today + "</p>");
  })
  

  // on remove selected component from dropped area
  $(document).on("click", ".remove_component", function(event){

    var el_component = $(this).closest(".card").get();
    DEBUG && console.log("component : ", el_component);

    var id_component = $(el_component).data("component-id");
    DEBUG && console.log("Removing component with id : ", id_component);

    var component_data = $(el_component).find(".component_data").get();
    DEBUG && console.log("component_data : ", component_data);

    //jQuery(jQuery(id_component_data_holder).find('#' + invoke_div).detach()).appendTo($(el));
    jQuery($(component_data).detach()).appendTo(jQuery(id_component_data_holder));

    // show label
    $(el_component).find(".component_label").removeClass("hidden");

    // get default position or rank
    var rank = $(el_component).data("position");
    if(rank == 'undefined')
    {
      console.log("data Position  is undefined  in : ", el_component);
      rank = -1;
    }

    // also add card to drag box
    //jQuery($(el_component).detach()).appendTo(jQuery("#"+ id_board_drag));
    jQuery("#"+ id_board_drag).insertAt(rank, $(el_component).detach());

    // remove data from table by making ajax call
    selected_component_remove(el_component);
  });

});


function after_element_drop(el, target, source, sibling)
{
  // source element id 
  var source_id = $(source).attr("id");
  DEBUG && console.log("Source element id is : ", source_id);

  // target element id
  var target_id = $(target).attr("id");
  DEBUG && console.log("Target element id is : ", target_id);

  // if (string1.toLowerCase() === string2.toLowerCase())
  //if ((target_id.toLowerCase() === id_board_drop) && (source_id.toLowerCase() === id_board_drag))
  if(target_id.toLowerCase() != source_id.toLowerCase())
  {
    // console.log("Id of source is 'on_hold' ");
    var invoke_div = $(el).data("invoke-div");  // ex. product_category
    DEBUG && console.log("invoke_div : ", invoke_div);

    // check is element exists 
    var len_invoke_div = $('#' + invoke_div).length
    DEBUG && console.log("Length of invoke div : ", len_invoke_div);

    // $(component_data_holder).find("#" + )

    if(len_invoke_div === 1)
    {
      // everything ok // process next step
      // hide original label of component
      $(el).find(".component_label").addClass("hidden");

      // append div to element
      // jQuery(jQuery("#yourElement").detach()).appendTo("body")
      jQuery(jQuery(id_component_data_holder).find('#' + invoke_div).detach()).appendTo($(el))
      
      // save selected element in table
      add_component_to_selected_list(el);

    }
    else if(len_invoke_div === 0)
    {
      console.log('Div with id : "'+ invoke_div + '" not found')
      alert('Div with id : "'+ invoke_div + '" not found')
    }
    else if(len_invoke_div > 1)
    {
      console.log("More than two div found with id : "+ invoke_div);
      $.confirm({
        title: 'Encountered an error!',
        content: "More than two div found with id : "+ invoke_div,
        type: 'red',
        typeAnimated: true,
      });
    }
  }
 return true;
}


function add_component_to_selected_list(el)
{
   var url = $("#url_add_selected_component").val();
   if(url == 'undefined')
   {
    DEBUG && console.log("Url undefined to component to selected list: ");
   }
   else
   {
    var id_campaign = $("#id_campaign").val();
    var id_selected_component = $(el).data("component-id");
    
    var ajaxTime= new Date().getTime();

   $.ajax({
       url: url,
       type: "POST",
       //dataType: "json",

       data: {
           id_campaign: id_campaign,  // "34",
           id_selected_component: id_selected_component,  // 1
       },

       /**
        * A function to be called if the request succeeds.
        */
       success: function(data) {
           var totalTime_in_ms = new Date().getTime() - ajaxTime;
           //console.log("Total time to complete ajax call : ", totalTime_in_ms ,' ms');
           var seconds = (totalTime_in_ms / 1000);
           console.log("Total time to complete ajax call : ", seconds, ' seconds');

           console.dir(data);
           console.dir(data.message);
           //alert("Data: " + data + "\nStatus: " + status);
       },

       /**
        * A function to be called if the request fails. 
        */
       error: function(jqXHR, textStatus, errorThrown) {
          show_ajax_error_info(jqXHR, textStatus, errorThrown);
       },

   });

 }
}


function selected_component_remove(el)
{
   var url = $("#url_remove_selected_component").val();
   if(url == 'undefined')
   {
    DEBUG && console.log("Url undefined to component to selected list: ");
   }
   else
   {
    var id_campaign = $("#id_campaign").val();
    var id_selected_component = $(el).data("component-id");
    
    var ajaxTime= new Date().getTime();

   $.ajax({
       url: url,
       type: "POST",
       //dataType: "json",

       data: {
           id_campaign: id_campaign,  // "34",
           id_selected_component: id_selected_component,  // 1
       },

       /**
        * A function to be called if the request succeeds.
        */
       success: function(data) {
           var totalTime_in_ms = new Date().getTime() - ajaxTime;
           //console.log("Total time to complete ajax call : ", totalTime_in_ms ,' ms');
           var seconds = (totalTime_in_ms / 1000);
           console.log("Total time to complete ajax call : ", seconds, ' seconds');

           console.dir(data);
           console.dir(data.message);
           //alert("Data: " + data + "\nStatus: " + status);
       },

       /**
        * A function to be called if the request fails. 
        */
       error: function(jqXHR, textStatus, errorThrown) {
          show_ajax_error_info(jqXHR, textStatus, errorThrown);
       },

   });

 }
}


function show_ajax_error_info(jqXHR, textStatus, errorThrown)
{
  //alert('An error occurred... Look at the console (F12 or Ctrl+Shift+I, Console tab) for more information!');

   console.log('jqXHR:');
   console.log(jqXHR);

   if (jqXHR.status == 500) 
   {
       // Server side error
       console.log("Server side Error");
   } 
   else if (jqXHR.status == 404)
   {
       // Not found
       console.log("Requested URL (page) not found");
   } 
   else if (jqXHR.status == 403) 
   {
       // Forbidden
       console.log("The request is for something forbidden. Authorization will not help.");
   } 
   else 
   {
       console.log("jqXHR.status : " + (jqXHR.status).toString() + " and errorThrown : " + errorThrown);
   }
}


// jQuery insert div as certain index
jQuery.fn.insertAt = function(index, element) {
  var lastIndex = this.children().size();
  if (index < 0) {
    index = Math.max(0, lastIndex + 1 + index);
  }
  this.append(element);
  if (index < lastIndex) {
    this.children().eq(index).before(this.children().last());
  }
  return this;
}