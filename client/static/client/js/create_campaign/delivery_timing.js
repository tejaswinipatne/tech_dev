
$(document).ready(function(){
  var DEBUG = true; // false

  $(document).on('change','.delivery_timing', function() {
    //$('input[name="' + this.name + '"]').not(this).prop('checked', false);
    var current_element = this;
    var checkbox_name = this.name;
    DEBUG && console.log("current element: " , current_element);

    var is_toggle_others_value = $(current_element).data("toggle_others_value");
    if(is_toggle_others_value)
    {
      if ($(current_element).is(':checked')) {
        // uncheck other checkboxs
        $('input[name="' + checkbox_name + '"]').not(this).prop('checked', false);
      }
    }

    var search_closet_parent = $(current_element).data("search_closet_parent");
    var closet_parent = undefined;
    if(search_closet_parent)
    {
      var parent_to_search_with_selector = undefined;

      var parent_search_by_class = $(current_element).data("parent_search_by_class");
      if(parent_search_by_class)
      {
        var parent_to_search_with_selector = "." + search_closet_parent;
      }

      var closet_parent = $(current_element).closest(parent_to_search_with_selector).get(0);

      if(closet_parent)
      {
        var val = $(current_element).val()
        // store type inside hidden input
        $(closet_parent).find("input[name='campaign_delivery_time_type']").val(val);
      }

      if(closet_parent == undefined)
      {
        console.log("Unable to find parent with name : " + search_closet_parent);
      }

    }
    else
    {
      DEBUG && console.log("set as false - so ignoring - search closet parent");
    }

    // if parent found process fruther
    if(closet_parent)
    {
      var toggle_parent_table = $(current_element).data("toggle_parent_table");
      if(toggle_parent_table)
      {
        // get parent first table
        var table = $(closet_parent).find("table").get(0);
        $(table).toggleClass("hidden");
        DEBUG && console.log("toggling parent div first table hidden class: " , table);
      }
      else
      {
        DEBUG && console.log("set as false - so ignoring - toggle parent table hidden class");
      }

      // if hide parent table set
      var hide_parent_table = $(current_element).data("hide_parent_table");
      if(hide_parent_table)
      {
        // get parent first table
        var table = $(closet_parent).find("table").get(0);
        DEBUG && console.log("hidding parent div first table : " , table);
        // hide table
        $(table).addClass("hidden");
      }
      else
      {
        DEBUG && console.log("set as false - so ignoring - hide parent table");
      }

      var table = $(closet_parent).find("table").get(0);
      var clear_table_input_data_on_hide = $(current_element).data("clear_table_input_data_on_hide");

      if(clear_table_input_data_on_hide)
      {
        if($(table).is(":visible"))
        {
            DEBUG && console.log("not clearing parent table input values because table is visible");
        }
        else {
          DEBUG && console.log("clearing parent table input values because table is hidden");
          // (":input") will select all inputs including select also
          $(table).find(":input").each(function(){
            $(this).val("");
          });
        }

      }
      else
      {
        DEBUG && console.log("clear_parent_table_input_data : " , clear_parent_table_input_data);
        DEBUG && console.log("set as false - so ignoring - clear parent table input values");
      }

    }

  });

  // serialize  data on input value change
  $(document).on('change','#table_delivery_timing :input', function() {
    var table = "#table_delivery_timing";
    var table_tr_inputs_data = table_tr_inputs_as_json(table);

    $(table).find("input[name='campaign_delivery_time']").val(table_tr_inputs_data);

  });

  // clone row
  $(document).on('click', ".clone-row", function(){
    DEBUG && console.log("Clone row Clicked");
    var current_element = this;
    var closest_tr = $(current_element).closest("tr").get(0);
    var cloned_row = $(closest_tr).clone();

    // clear cloned row input values
    $(cloned_row).find(":input").val(""); // all row inputs

    // append to table body
    var tbody = $(current_element).closest("tbody").get(0);
    $(tbody).append(cloned_row);

  });

  // remove row
  $(document).on('click', ".remove-row", function(){
    DEBUG && console.log("remove-row row Clicked");
    var current_element = this;
    var closest_tr = $(current_element).closest("tr").get(0);
    $(closest_tr).remove();
  });

});

function table_tr_inputs_as_json(table)
{
  var json = undefined;
  var row_data = {};
  var table_data = [];

  $(table).find("tbody tr").each(function(){

    $(this).find(":input:visible").each(function(){
      //console.log(this);
      var name= $(this).attr("name");
      var val = $(this).val();

      row_data[name] = val;
    });

    //console.log("row_data : ", row_data);
    table_data.push(row_data);
  });

  console.log("table data : ", table_data);
  return table_data;
}
