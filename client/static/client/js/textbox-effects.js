
// https://codepen.io/Takumari85/pen/RaYwpJ

// JavaScript for label effects only
	$(window).load(function(){
		//$(".col-3 input").val("");

		$(".input-effect input").focusout(function(){
			if($(this).val() != ""){
				$(this).addClass("has-content");
			}else{
				$(this).removeClass("has-content");
			}
		})
	});
