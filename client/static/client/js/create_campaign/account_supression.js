if (typeof DEBUG === 'undefined')
	var DEBUG = true;  // false


$(function () {
	// on file upload
	//$("input:file").change(function (){
	$(".data_file").change(function () {

		var $fileName = $(this).val();
		DEBUG && console.log("$filename:", $fileName);

		$url = $(this).data("url-save-data");
		DEBUG && console.log("url to save file : ", $url);

		// You need to use standard javascript object here for formdata
		// var form = $(this).closest("form")[0]; // or get(0)
		var $form = $(this).closest("form").get(0);
		DEBUG && console.log("form : ", $form);

		var $form_data = new FormData($form); //Creates new FormData object

		//append campaign id to form data
		var $id_campaign = $("#id_campaign").val();
		DEBUG && console.log("$id_campaign : ", $id_campaign);

		// $form_data.append("id_campaign", "Groucho");
		$form_data.append("id_campaign", $id_campaign);

		// get field name and append to form data
		var $field_name = $(this).attr("name");
		DEBUG && console.log("$field_name : ", $field_name);
		$form_data.append("field_name", $field_name);

		if (DEBUG) {
			for (var [key, value] of $form_data.entries()) {
				console.log(key, value);
			}
		}


		if ($url || $id_campaign) {
			// make ajax call and save data
			$.ajax({
				context: document.body, // access form inside
				url: $url, //'/ajax/validate_username/',
				type: "POST",
				data: $form_data,
				processData: false,  // tell jQuery not to process the data
				contentType: false,  // tell jQuery not to set contentType

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
					console.log(msg);
					$.confirm({
						title: 'Encountered an error!',
						content: msg,
						type: 'red',
						typeAnimated: true,
					});
				},
			})

			// hide previous_selected_file div
			$(this).closest("form").parent().find(".previous_selected_file").addClass("hidden");
		}
		else {
			console.log("Skipping ajax call because either $url or $id_campaign is empty");
		}


	});
});