$(function(){
  $(".search_table").on("keyup", function() {
    var value = $(this).val();

    var parent = $(this).data("parent");
    if(parent)
    {
        $(this).closest("." + parent).find("table tr").each(function(index) {
            if (index !== 0) {
    
                $row = $(this);
    
                var id = $row.find("td:first").text().toLowerCase();
    
                if (id.search(value.toLowerCase()) == -1) {
                    $row.hide();
                }
                else {
                    $row.show();
                }
            }
        });
    }
    else
    {
        console.log("Input with '.search_table' class has no data attribute parent(Parent is used to find table)")
    }
 });
})