$(function(){

  //
  $(document).on('click','.btn_process_before_save_form', function() {
    // calculate days between start date and end date to set set_priority
    console.log("btn_process_before_save_form clicked");

    //get selected start date
    var start_date = $(this).parents("form").find("input[name='start_date']").val();
    console.log("start date : ", start_date);

    //get selected end date
    var end_date = $(this).parents("form").find("input[name='end_date']").val();
    console.log("end date : ", end_date);

    //get differencs
    var a = moment(end_date) //moment([2015, 11, 29]);
    var b = moment(start_date) //moment([2007, 06, 27]);

    var days = a.diff(b, 'days');
    console.log('days difference : ' + days);

    if(days>=0 & days<= 10)
    {
      console.log("Hign priority lead");
      priority = "High";
    }
    else if(days>10 & days<=30)
    {
      console.log("Medium priority lead");
      priority = "Medium";
    }
    else if(days>30)
    {
      console.log("Low priority lead");
      priority = "Low";
    }

    // set priority to element
    $(this).parents("form").find("input[name='priority']").val(priority);
    console.log("This form element priority : ");
    console.log($(this).parents("form").find("input[name='priority']").val());

    // trigger submit button click
    var disabled = $(this).parent().find(".btn_save_form").is(":disabled");
    if(disabled)
    {
      // dont trigger click of form save button
    }
    else
    {
      $(this).parent().find(".btn_save_form").trigger("click");
    }

  });

});
