
$(function () {

  dragula([document.querySelector('#grid1'), document.querySelector('#grid2')]
   ).on('drag', function (el) {
     //console.log(el);
   }).on('drop', function (el, target, source) {
     //console.log(el);
     //console.log(target); // grid2
     //console.log(source); // grid1
     //console.log($(el).text());
     grid_to_fetch_vals = "#grid2";
     element_to_find = ".card";
     data_attribute = "header";
     var concatcated_str = get_grid_values(grid_to_fetch_vals, element_to_find, data_attribute);

     // store value inside hidden input
     var parent = "#row_data_header";
     var input= 'input[type="hidden"]';
     var value = concatcated_str;
     store_val_in_hidden_input(target, parent, input, value)
   })

});

function get_grid_values(grid, element_to_find, data_attribute)
{
  var selected_values = [];
  $(grid).find("").each(function(){
    var data = $(this).data(data_attribute); // data_attribute - ex. data-header
    //console.dir(data);
    selected_values.push(data);
  });

  //console.dir(selected_values);
  var concatcated_str = selected_values.join();
  console.dir("concatcated_str");
  console.dir(concatcated_str);

  return concatcated_str;
}

function store_val_in_hidden_input(current_element, parent, input, value)
{
  var parent_element = $(current_element).closest(parent).get(0);
  //console.log("parent_element :"); console.dir(parent_element);

  var input_element = $(parent_element).find(input).get(0);
  //console.dir("input element :"); console.dir(input_element);

  $(input_element).val(value);

  var input_value= $(input_element).val();
  console.log("input_value : "); console.dir(input_value);

  return true;
}
