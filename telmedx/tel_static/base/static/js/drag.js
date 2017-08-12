//global variables
var resizeWidth = 0;
var resizeHeight = 0;
var resizeWidthRight = 0;
var resizeHeightRight = 0;
$(document).ready(function () {
    console.log("ready!");
    // Optimalisation: Store reference outside the event handler:
    var $window = $(window);
    /* Execute on load */
    checkWidth();
    locateStream();
    // Bind event listener
    //$(window).resize(checkWidth);
    $(window).resize(function () {
	console.log("window resized");
	checkWidth();
        $(".resizable").resizable("option", "maxHeight", resizeHeight);
        $(".resizable").resizable("option", "maxWidth", resizeWidth);
        $(".resizable-right").resizable("option", "maxHeight", resizeHeightRight);
        $(".resizable-right").resizable("option", "maxWidth", resizeWidthRight);
    });

    function checkWidth() {
        var windowsize = $window.width();
        if (windowsize < 992) {
            //if the window is less than 992px wide then...
            resizeHeight = 500;
            resizeWidth = $window.width() - 30;
            resizeHeightRight = 800;
            resizeWidthRight = $window.width() - 30;
        } else {
            resizeHeight = 420;
            resizeWidth = 600;
            resizeWidthRight = $(".col-md-6").width();
            resizeHeightRight = 800;
        }
    }

    function locateStream() {
        /*
         * This function is to allow or disable resizing of the container before stream has loaded in
        */
        // see if stream elementExists
        // if it does not, disable resizing?
        var elementExists = document.getElementById("hollywood");
        if (elementExists == null) {
            console.log("Cannot find hollywood");
        } else {
            console.log("hollywood exists");
        }
    }

    function checkoverflow(ele) {
        var element = document.querySelector('' + ele);
        console.log("checkoverflow called");
        if (element.offsetHeight < element.scrollHeight ||
            element.offsetWidth < element.scrollWidth) {
            // your element have overflow
            console.log("element has overflow");
        } else {
            // your element doesn't have overflow
            console.log("element is fine");
        }
    }

    $(".resizable").resizable({
        aspectRatio: false,
        handles: "se",
        maxHeight: function () {
            return resizeHeight;
        },
        maxWidth: function () {
            return resizeWidth;
        },
        minHeight: 300,
        minWidth: 250,
    });
    $(".resizable-right").resizable({
	minHeight: 500,
        minWidth: 500,
        maxHeight: resizeHeightRight,
        maxWidth: resizeWidthRight
    });
    //$( ".stream-container" ).width();
    $(".ui-icon-gripsmall-diagonal-se").mousedown(function () {
        console.log("resizable clicked");
        checkWidth();
        $(".resizable").resizable("option", "maxHeight", resizeHeight);
        $(".resizable").resizable("option", "maxWidth", resizeWidth);
        $(".resizable-right").resizable("option", "maxHeight", resizeHeightRight);
        $(".resizable-right").resizable("option", "maxWidth", resizeWidthRight);
    });
});

