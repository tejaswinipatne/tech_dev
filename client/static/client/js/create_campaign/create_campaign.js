<!-- Create campaign js -->
$(document).ready(function() {
    function toggleIcon(e) {
        $(e.target)
            .prev('.panel-heading')
            .find(".more-less")
            .toggleClass('glyphicon-plus glyphicon-minus');
    }
    $('.panel-group').on('hidden.bs.collapse', toggleIcon);
    $('.panel-group').on('shown.bs.collapse', toggleIcon);
});

// waterfall
$(document).ready(function() {
    $("#waterfalltable").hide();
    $("#watercheck").click(function() {

        var isChecked = $('#watercheck').prop('checked');
        if (isChecked) {
            $("#waterfalltable").show();
        } else {
            $("#waterfalltable").hide();
        }
    });

});

$(document).ready(function() {

    $(".tbl").hide();

    $(".delivery_timing")
        .change(function() {
            var count = 0;
            var fav = [];

            $.each($("input[name='delivery_timing']:checked"), function() {
                count = count + 1;
            });

            if (count == 2) {
                $(".tbl").hide();
                alert('Only One Option Can Be Selected');
            }
            if (count == 1) {
                $.each($("input[name='delivery_timing']:checked"), function() {
                    fav.push($(this).val());

                });
                var temp = "";
                fav.forEach(function(element) {
                    temp = element;
                });

                if (temp == "Batch") {

                    $(".tbl").show();
                } else {
                    $(".tbl").hide();
                }

            }

        });

    $(".slt")
        .change(function() {

            var favorite = [];

            $.each($("input[name='sport']:checked"), function() {
                favorite.push($(this).val());

            });
            if (favorite.length != 0) {
                $(".txt").text("Selected Header:");
            }
            var str = '';
            favorite.forEach(function(element) {
                str = str + "<th>" + element + "</th>";
            });

            $(".slt1").html(str);
        });

    $(".qt1").hide();
    $(".chk").change(function() {
        $(".qt1").toggle();
    });

    $(".sa").change(function() {

        var favorite = [];

        $.each($("input[name='sport']:checked"), function() {
            favorite.push($(this).val());

        });
        if (favorite.length != 0) {
            $(".txt").text("Selected Header:");
        }
        var str = '';
        favorite.forEach(function(element) {
            str = str + "<th>" + element + "</th>";
        });

        $(".slt1").html(str);
    });
});

$(document).ready(function() {
    var $sourceFields = $("#sourceFields");
    var $destinationFields = $("#destinationFields");
    var $chooser = $("#fieldChooser").fieldChooser(sourceFields, destinationFields);
});

$("#dragdiv li").draggable({
    helper: "clone",
    cursor: "move",
    revert: "invalid"
});

initDroppable($("#dropdiv"));

function initDroppable($elements) {
    $elements.droppable({
        activeClass: "ui-state-default",
        hoverClass: "ui-drop-hover",
        accept: ":not(.ui-sortable-helper)",

        over: function(event, ui) {
            var $this = $(this);
        },
        drop: function(event, ui) {
            var $this = $(this);
            if ($this.val() == '') {
                $this.val(ui.draggable.text().trim());
            } else {
                $this.val($this.val() + "," + ui.draggable.text().trim());
            }
        }
    });

}

//
// checkbx_toggle_use_as_txt
$(document).ready(function() {
    $(document).on("click", ".checkbx_toggle_use_as_txt", function() {
        console.log(" checkbx_toggle_use_as_txt clicked");
        // find parent ul of checkbox
        var ul_parent = $(this).parents(ul);
        console.log("ul Parent");
        console.dir(ul_parent);

        $(ul_parent).find(".use_as_txt").toggleClass("hidden");

    });
});
