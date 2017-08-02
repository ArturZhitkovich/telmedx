//global variables
var resizeWidth = 0;
var resizeHeight = 0;
var resizeWidthRight = 0;
var resizeHeightRight = 0;
$(document).ready(function () {
    console.log("ready!");
    // Optimalisation: Store reference outside the event handler:
    var $window = $(window);

    function checkWidth() {
        var windowsize = $window.width();
        if (windowsize < 992) {
            //if the window is less than 992px wide then...
            resizeHeight = 1200;
            resizeWidth = $window.width() - 30;
            resizeHeightRight = 800;
            resizeWidthRight = $window.width() - 30;
        } else {
            resizeHeight = 800;
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
        aspectRatio: true,
        handles: "se",
        maxHeight: resizeHeight,
        maxWidth: resizeWidth,
        minHeight: 500,
        minWidth: 250,
    });
    $(".resizable-right").resizable({
        minHeight: resizeHeightRight,
        maxWidth: resizeWidthRight
    });
    /* Execute on load */
    checkWidth();
    locateStream();
    // Bind event listener
    $(window).resize(checkWidth);
});
