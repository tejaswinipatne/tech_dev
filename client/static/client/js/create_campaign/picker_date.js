/* ------------------------------------------------------------------------------
*
*  # Date and time pickers
*
*  Specific JS code additions for picker_date.html page
*
*  Version: 1.1
*  Latest update: Aug 10, 2016
*
* ---------------------------------------------------------------------------- */

$(function() {


    // Pick-a-date picker
    // ------------------------------


    // Format options
    $('.pickadate-format').pickadate({

        // Escape any “rule” characters with an exclamation mark (!).
        format: 'dddd, dd mmm, yyyy',
        formatSubmit: 'yyyy/mm/dd',
		
		// allow year dropdown selection
		selectYears: true,
        selectMonths: true,
		
		// disable past dates
		min: +2,
		
		// The picker footer
		footer: 'picker__footer',
    });

});
