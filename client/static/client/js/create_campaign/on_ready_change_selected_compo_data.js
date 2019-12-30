if(typeof DEBUG === 'undefined')
      var DEBUG =  true;  // false


$(document).ready(function(){

	DEBUG && console.log("Changing content of selected component ");

	// iterate in each board3 card 
	$("#board3").find(".card").each(function(){

		var invoke_div = $(this).data("invoke-div");
		DEBUG && console.log("invoke_div : ", invoke_div)

		if(invoke_div != 'undefined')
		{
			// check is element exists 
		    var len_invoke_div = $('#' + invoke_div).length
		    DEBUG && console.log("Length of invoke div : ", len_invoke_div);

		    // $(component_data_holder).find("#" + )

		    if(len_invoke_div === 1)
		    {
		      // everything ok // process next step
		      // hide original label of component
		      $(this).find(".component_label").addClass("hidden");

		      // append div to element
		      // jQuery(jQuery("#yourElement").detach()).appendTo("body")
		      jQuery(jQuery(id_component_data_holder).find('#' + invoke_div).detach()).appendTo($(this));

		    }
		    else if(len_invoke_div === 0)
		    {
		      console.log('Div with id : "'+ invoke_div + '" not found')
		      //alert('Div with id : "'+ invoke_div + '" not found')
		    }
		    else if(len_invoke_div > 1)
		    {
		      console.log("More than two div found with id : "+ invoke_div);
		      //alert("More than two div found with id : "+ invoke_div);
		      $.confirm({
				    title: 'Encountered an error!',
				    content: "More than two div found with id : "+ invoke_div,
				    type: 'red',
				    typeAnimated: true,
			  });
		    }
		}
		else
		{
			DEBUG && console.log(" component card : ", this, " has no any attribute value");
		}
	});

});