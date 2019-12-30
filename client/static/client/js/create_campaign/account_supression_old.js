// account supression
// supression

$(function(){

	// select element from iD
	var radio_abm_yes = '#radio_abm_yes'; //Account Based Marketing radio yes button
	var radio_abm_no = '#radio_abm_no'; //Account Based Marketing radio no button
	var button_abm_upload = '#button_abm_upload'; //Account Based Marketing radio no button

	var radio_acc_suppression_yes = '#radio_acc_suppression_yes'; //Account supression radio yes button
	var radio_acc_suppression_no = '#radio_acc_suppression_no'; //Account supression radio no button
	var button_abm_upload = '#button_abm_upload'; //Account supression radio no button

	// on click of
	//Account Based Marketing radio yes button
	$(document).on( "change", radio_abm_yes , function(){
		//alert("radio_abm_yes changed");
		// display upload button
		$(radio_abm_no).prop('checked',false);
		$(button_abm_upload).css({ "display":"block" });
		$(radio_acc_suppression_yes).prop('disabled','disabled');
		$(radio_acc_suppression_no).prop('disabled','disabled');
		$(button_acc_supression).css({ "display":"none" });
	});

	// on click of
	//Account Based Marketing radio no button
	$(document).on( "change", radio_abm_no , function(){
		//alert("radio_abm_no changed");
		// display upload button
		$(radio_abm_yes).prop('checked',false);
		$(button_abm_upload).css({ "display":"none" });
		$(radio_acc_suppression_yes).prop('disabled','');
		$(radio_acc_suppression_no).prop('disabled','');

	});


	// on click of
	//Account Suppression radio yes button
	$(document).on( "change", radio_acc_suppression_yes , function(){
		//alert("radio_acc_suppression_yes changed");
		// display upload button
		$(radio_acc_suppression_no).prop('checked',false);
		$(button_acc_supression).css({ "display":"block" });

	});

	// on click of
	//Account Suppression radio no button
	$(document).on( "change", radio_acc_suppression_no , function(){
		//alert("radio acc suppression changed");
		// display upload button
		$(radio_acc_suppression_yes).prop('checked',false);
		$(button_acc_supression).css({ "display":"none" });
	});

});
