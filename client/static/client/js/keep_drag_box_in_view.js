//keep element in view
(function($)
{
    $(document).ready( function()
    {
		var element_to_fix = $(".fixed_box")[0];
		
		if(element_to_fix != undefined)
		{
			// get first top postion of element
			var elementPosTop = $(element_to_fix).position().top;
		
			$(window).scroll(function()
			{
				if ($(window).width() > 960) 
				{
					var wintop = $(window).scrollTop(), docheight = $(document).height(), winheight = $(window).height();
					console.log("wintop :", wintop);
					
					var scroll_amt = wintop - elementPosTop;
					$(element_to_fix).css({ "margin-top": scroll_amt });
				}
				
			});
		}
		
    });
})(jQuery);