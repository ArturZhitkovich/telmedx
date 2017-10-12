const $ = require('jquery');
const panzoom = require('jquery.panzoom');
const jqueryUi = require('jquery-ui-bundle');


module.exports = {
    $el: null,

    //Frame counter & UI
    ff: 0,
    lastFrame: 0,
    fCounter: 0,
    startTime: new Date(),

    //video feed rotation
    //Default Rotation
    rotate: 90,
    ctx: null,
    canvas: null,

    // Stream box & Device
    streamBox: null,
    deviceName: null,

    // large image rotation
    ctx2: null,
    canvas2: null,

    // Canvas support
    // true or false, defines if we should use canvas or img
    canvasSupport: null,

    // Sketchpad
    sketchpad: null,

    // Flash
    isFlashOn: false,
    flashToggeling: false,

    // Camera
    frontCamera: false,
    cameraToggeling: false,

    // Caputred Image Viewer
    $section: null,
    controlOutput: null,

    resizeWidth: 0,
    resizeHeight: 0,
    resizeWidthRight: 0,
    resizeHeightRight: 0,


    init(el) {
        this.$el = $(el);

        if (this.$el.length) {
            this.bindUiActions();
            this.frameOne_jq();
        }
    },

    iePolyfill: function () {
        // IE 8 Fix for IndexOf
        if (!Array.prototype.indexOf) {
            Array.prototype.indexOf = function (elt /*, from*/) {
                let len = this.length >>> 0,
                    from = Number(arguments[1]) || 0;

                from = (from < 0)
                    ? Math.ceil(from)
                    : Math.floor(from);

                if (from < 0) {
                    from += len;
                }

                for (; from < len; from++) {
                    if (from in this && this[from] === elt) {
                        return from;
                    }
                }
                return -1;
            };
        }
    },

    bindUiActions() {
        const context = this;
        this.$section = $('#capture-snaper').first();

        this.deviceName = $("#deviceName").data('name');

        this.$section.find('.panzoom').panzoom({
            $zoomIn: this.$section.find(".zoom-in"),
            $zoomOut: this.$section.find(".zoom-out"),
            $zoomRange: this.$section.find(".zoom-range"),
            $reset: this.$section.find(".reset")
        });

        $("#open-editor").click(function () {
            const $editSnapshot = $('#editSnapshot');
            const $drawingLayer = $('#drawing-layer');

            setTimeout(function () {
                $editSnapshot.removeClass('hundo');
                $editSnapshot.attr('src', $("#activeSnapshot").attr('src'));

                const marginleft = ($editSnapshot.parent(".modal-body").innerWidth() - $editSnapshot.innerWidth()) / 2;
                $editSnapshot.css("margin-left", marginleft);

                $drawingLayer.css("marginleft", marginleft);
                $drawingLayer.css("height", $editSnapshot.height());
                $drawingLayer.css("width", $editSnapshot.width());
            }, 1000);
        });

        $("#flash-toggle").click(function () {
            if (context.flashToggeling || context.frontCamera || context.cameraToggeling) {
                return;
            }

            context.toggle_jq();
            if (context.isFlashOn) {
                context.flashOff();
            } else {
                context.flashOn();
            }
        });

        //$("#flash-toggle").css("width", $("#flash-toggle").outerWidth());

        $(window).resize(function () {
            context.sizePreview();
        });

        this.sizePreview();

        $("#camera-toggle").click(function () {
            if (context.cameraToggeling) {
                console.log('I\'m toggleing');
                return;
            }
            context.flashOff();
            context.toggle_camera_jq();
            if (!context.frontCamera) {
                // $("#camera-toggle div:not('#camera-front-icon')").hide();
                $("#flash-toggle").addClass('disabled');
            } else {
                // $("#camera-toggle div:not('#camera-back-icon')").hide();
                $("#flash-toggle").removeClass('disabled');
            }
        });

        $('#myModal').bind('hidden.bs.modal', function () {
            $("html").css("margin-right", "0px");
        });

        $('#myModal').bind('show.bs.modal', function () {
            $("html").css("margin-right", "-15px");
        });

        $("#rotate-right").click(function () {
            var angle = ($('#hollywood').data('angle') + 90) || 90;
            $('#hollywood').css({'transform': 'rotate(' + angle + 'deg)'});
            $('#hollywood').data('angle', angle);
        });

        $("#rotate-left").click(function () {
            var angle = ($('#hollywood').data('angle') - 90) || - 90;
            $('#hollywood').css({'transform': 'rotate(' + angle + 'deg)'});
            $('#hollywood').data('angle', angle);
        });

        $("#capture-button").click(function () {
            context.takeSnapshotClicked();
        });

        $("#delete-snapshot").click(function () {
            context.deleteSnapshot();
        });

        $('div').on('click', '.closeDiv', function () {
            var snapDeleteID = $(this).attr("id");
            var snapID = snapDeleteID.replace('delete-','')
            $("#" + snapID).remove();
            $("#" + snapDeleteID).remove();
            $('.' + 'container-'+ snapID).remove();
            console.log("item deleted");
        });


        this.canvasSupport = this.isCanvasSupported();
        const $stream = $('#stream');
        if (!this.canvasSupport) {
            $("#c").remove();
            $stream.html('<img id="hollywood" src="/static/img/controls/spinner.gif" />');
        } else {
            this.canvas = document.getElementById("video-canvas");
            this.ctx = this.canvas.getContext('2d');
            this.canvas2 = document.getElementById("b");
            this.ctx2 = this.canvas2.getContext('2d');
        }

        $stream.css("overflow", "hidden");
        if ($('html').hasClass('lt-ie9')) {
            $("#rotate-buttons").css("visibility", "hidden");
            $("#zoom-controls").css("visibility", "hidden");
        }

        // Bind pastSnapshots for future snapshots
        $('#pastSnapshots').on('click', '.snap-item', function(ev) {
            // Snapshot id
            const sid = $(ev.target).data('sid');
            context.showSnapshot(sid);
        });

        this.bindResizeEvents();
    },

    isCanvasSupported() {
        return false;
        const elem = document.createElement('canvas');
        return !!(elem.getContext && elem.getContext('2d'));
    },

    inviteClicked() {
        $.post("/ttux/invite");
    },

    // adds border to snapshot 
    select(id) {
        $(".snapshot").css("border", "none");
        $("#" + id).css("border", "4px solid");
        this.$section.find('.panzoom').panzoom("reset");
    },

    showSnapshot(id) {
        const selected = $("#" + id);
        $("#activeSnapshot").attr("src", selected.attr("src"));
        this.select(id);
    },

    deleteSnapshot(id) {
        console.log("Snapshot deleted");
    },

    makeid() {
        const possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        let text = "";

        for (let i = 0; i < 15; i++) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }

        return text;
    },

    toggle_jq() {
        const context = this;
        this.flashToggeling = true;

        $.ajax({
            url: "/ttux/flashlight/" + this.deviceName
        }).done(function (data) {
            console.log(data);
            context.flashToggeling = false;
            if (data.status === 'on') {
                context.flashOn();
            } else if (data.status === 'off') {
                context.flashOff();
            } else {
                console.log("Something went wrong with the flash");
            }
        });
    },

    takeSnapshotClicked() {
        const context = this;
        let ie = !!$('html').hasClass('lt-ie9');

        $.post("/ttux/snapshot/" + this.deviceName, {'ie': ie}, function (data) {
            let dataUri;
            if (ie) {
                dataUri = '/ttux/ie-snapshot/' + context.deviceName + '/' + context.makeid();
            } else {
                dataUri = "data:image/jpeg;base64," + data.image;
            }

            if (context.canvasSupport && !ie) {
                const image = new Image();
                image.src = dataUri;
                image.onload = function () {
                    let cw = image.width, ch = image.height, cx = 0, cy = 0,
                        ratio = cw / ch;
                    //Calculate new canvas size and x/y coorditates for image
                    switch (context.rotate) {
                        case 90:
                            cw = image.height;
                            ch = image.width;
                            cy = image.height * (-1);
                            break;
                        case 180:
                            cx = image.width * (-1);
                            cy = image.height * (-1);
                            break;
                        case 270:
                            cw = image.height;
                            ch = image.width;
                            cx = image.width * (-1);
                            break;
                    }
                    console.log(context.rotate);

                    //Rotate image
                    context.canvas2.setAttribute('width', cw);
                    context.canvas2.setAttribute('height', ch);
                    context.ctx2.rotate(rotate * Math.PI / 180);
                    context.ctx2.drawImage(image, cx, cy);//Display Image in Canvas
                    dataUri = context.canvas2.toDataURL();

                    $("#activeSnapshot").attr("src", dataUri);
                    //Center the image
                    $("#activeSnapshot").css("margin-left", ($("#snapshots").innerWidth() - $("#activeSnapshot").innerWidth()) / 2);
                    const id = "snapshot-" + new Date().getTime().toString();
                    if (context.rotate === 90 || context.rotate === 270) {
                        smwidth = 45;
                        smheight = 45 * ratio;
                    } else {
                        smwidth = 45 * ratio;
                        smheight = 45;
                    }

                    var imageElement = $.parseHTML("<img class=\"snapshot-item snapshot\" id=\"" + id + "\" src=\"" + dataUri + "\" width=\"" + String(smwidth) + "\" height=\"" + String(smheight) + "\" onclick=\"window.parent.showSnapshot('" + id + "')\">");
                    
                    var container = document.createElement("div");
                    // maybe make class unique, or an id via the const id above
                    container.setAttribute('class', 'container-'+ id);
    
                    var div = document.createElement("div");
                    //div.innerHTML = "&times";
                    div.setAttribute('class', 'closeDiv');
                    div.setAttribute('id', "delete-" + id);

                    const $container = $(container);
                    $container.append(imageElement);
                    $container.append(div);
    
                    $("#pastSnapshots").append($container);

                    context.select(id);
                };
            } else {
                $("#activeSnapshot").attr("src", dataUri);
                context.$section.find('.panzoom').panzoom("reset");
                const id = "snapshot-" + new Date().getTime().toString();

                var imageElement = $.parseHTML(`<img data-sid="${id}" class="snap-item snapshot" id="${id}" src="${dataUri}" style="float:left;" width="75" height="50">`);                
            
                var container = document.createElement("div");
                // maybe make class unique, or an id via the const id above
                container.setAttribute('class', 'container-'+ id);

                var div = document.createElement("div");
                //div.innerHTML = "&times";
                div.setAttribute('class', 'closeDiv');
                div.setAttribute('id', "delete-" + id);

                const $container = $(container);
                $container.append(imageElement);
                $container.append(div);

                $("#pastSnapshots").append($container);

                context.select(id);
            }
        });
    },

    /**
     * Contains the main logic for requesting and processing command and image
     * frames requested from the server.
     */
    frameOne_jq() {
        const context = this;

        $.ajax({//Go get frame
            url: `/ttux/lastFrame/${this.deviceName}/${this.lastFrame}`
        }).done(function (msg) {
            // console.log(msg.substring(0,15));
            let fnumber = msg.substring(0, 8);
            let begin_img_data = 8;

            if (msg.substring(0, 2) === '!!') {
                let begin_end = msg.indexOf('!!', 2);
                let control = $.parseJSON(msg.substring(2, parseInt(begin_end, 10)));
                context.controlOutput = control;

                if (control.command === 'update_controls' && !$("html").hasClass("lt-ie9")) {
                    if (control.parameters.indexOf('flash') !== -1) {
                        console.log('flash');
                        $("#flash-toggle").show();
                    }
                    if (control.parameters.indexOf('flip') !== -1) {
                        console.log('flip');
                        $("#camera-toggle").show();
                    }
                }

                fnumber = msg.substring(parseInt(begin_end, 10) + 2, parseInt(begin_end, 10) + 10);
                console.log(context.fnumber);
                begin_img_data = parseInt(begin_end, 10) + 10;
                console.log(begin_img_data);
            }

            context.lastFrame = fnumber;

            if (msg.substring(8).length > 0) {
                let videoSrc = "data:image/jpg;base64," + msg.substring(begin_img_data);

                if (context.canvasSupport) {
                    const image = new Image();
                    image.src = videoSrc;

                    image.onload = function () {
                        let cw = image.width, ch = image.height, cx = 0, cy = 0;
                        // Calculate new canvas size and x/y coorditates for image
                        switch (context.rotate) {
                            case 90:
                                cw = image.height;
                                ch = image.width;
                                cy = image.height * (-1);
                                break;
                            case 180:
                                cx = image.width * (-1);
                                cy = image.height * (-1);
                                break;
                            case 270:
                                cw = image.height;
                                ch = image.width;
                                cx = image.width * (-1);
                                break;
                        }
                        //  Rotate image
                        context.canvas.setAttribute('width', cw);
                        context.canvas.setAttribute('height', ch);
                        context.ctx.rotate(context.rotate * Math.PI / 180);

                        //Scales the image down if it won't fit in the box
                        if (cw > context.streamBox.innerWidth()) {
                            context.ctx.scale(context.streamBox.innerWidth() / cw, context.streamBox.innerWidth() / cw);
                            // streamBox.css("height",ch*streamBox.innerWidth()/cw+"px");
                        }

                        context.ctx.drawImage(image, cx, cy);//Display Image in Canvas
                    };
                } else { //If canvas is not supported display in img tag
                    $("#hollywood").attr('src', videoSrc);
                }

                let now = new Date();
                let min = Math.floor((now - context.startTime) / 1000);
                let sec = (now - context.startTime) % 1000;

                $("#stream_status").html(min + "." + sec + " f: " + context.fCounter);
                context.fCounter++; //Adds to frame couter
            }

            context.frameOne_jq(); //Let the function call itself
        })//.error(function (msg) {
        // console.log("got error");
        // setTimeout("frameOne_jq()", 500);
        // });

    },

    toggle_camera_jq() {
        const context = this;
        this.cameraToggeling = true;

        $.ajax({
            url: "/ttux/flipcamera/" + this.deviceName
        }).done(function (data) {
            console.log(data);
            context.cameraToggeling = false;
            if (data.status === 'front') {
                context.frontCamera = true;
                $("#camera-front-icon").show();
                $("#flash-toggle").addClass('disabled');

            } else if (data.status === 'back') {
                context.frontCamera = false;
                $("#camera-back-icon").show();
                $("#flash-toggle").removeClass('disabled');

            } else {
                console.log("Something went wrong with the camera");
            }
        });
    },

    sizePreview() {
        if ($("body").innerWidth() > 992) {
            let snaperh = $(window).height() - 110 - 30;
            $("#capture-snaper").css("height", snaperh);
            $("#cap-body").css("height", snaperh - $("#cap-head").outerHeight());
        } else {
            $("#cap-body").css("height", "400px");
        }
    },

    flashOn() {
        this.isFlashOn = true;
        $("#flash-toggle").html('<img style="height: 25px;" src="/static/img/controls/open103off.png">');
        $("#flash-toggle").removeClass('active');
    },

    flashOff() {
        this.isFlashOn = false;
        $("#flash-toggle").html('<img style="height: 25px;" src="/static/img/controls/open103.png">');
        $("#flash-toggle").removeClass('active');
    },

    /**
     * Function to check the width on resize on the entire window.
     * To be used for adjusting the panel layouts depending on resolution.
     */
    checkWidth() {
        const $window = $(window);
        const windowsize = $window.width();

        if (windowsize < 992) {
            //if the window is less than 992px wide then...
            //this.resizeHeight = 650;
            this.resizeWidth = $window.width() - 30;
            //this.resizeHeightRight = 530;
            this.resizeWidthRight = $window.width() - 30;
        } else {
            //this.resizeHeight = 650;
            this.resizeWidth = 885;
            this.resizeWidthRight = 892.5;
            //this.resizeHeightRight = 650;

            //this.resizeWidthRight = $(".col-md-6").width();
            //this.resizeHeightRight = 800;
        }
    },

    locateStream() {
        /*
         * This function is to allow or disable resizing of the container before stream has loaded in
        */
        // see if stream elementExists
        // if it does not, disable resizing?
        const elementExists = $('#hollywood');
        if (!elementExists) {
            console.log("Cannot find hollywood");
        } else {
            console.log("hollywood exists");
        }
    },

    checkoverflow(el) {
        const element = document.querySelector('' + ele);
        console.log("checkoverflow called");
        if (element.offsetHeight < element.scrollHeight ||
            element.offsetWidth < element.scrollWidth) {
            // your element have overflow
            console.log("element has overflow");
        } else {
            // your element doesn't have overflow
            console.log("element is fine");
        }
    },

    /**
     * Bindings to adjust layout based on window size.
     */
    bindResizeEvents() {
        // Window resizing adjustments
        const $resizable = $('.resizable');
        const $resizableRight = $('.resizable-right');

        //this.checkWidth();
        this.locateStream();

        $(window).resize(function(){
            //this.checkWidth();
            console.log("window resize here");
            $resizable.css("width",$('.resizable').parent().css("width")-20);
            $resizableRight.css("width",$('.resizable-right').parent().css("width")-20); 

            var percent = ($(window).width()/100) * 48;
            console.log("percentpixel: " + percent);

            checkoverlap();
        });


        /**
         * Checks if videoStream container and Snapshot viewer are overlapping 
         */
        function checkoverlap() {
            var positionLeft = $resizable.offset().left + $resizable.width();
            var positionRight = $resizableRight.offset().left ;

            console.log("leftWidth: " + positionLeft);
            console.log("right: " + positionRight);

            if (positionLeft > positionRight) {
                // overlapping = TRUE       
                console.log("overlapping!");
                //$resizable.css("width",$('#video-container').css("width")-20);
                //$resizableRight.css("width",$('#snap-container').css("width")-20); 

                //checkWidth();
                //$resizable.resizable("option", "maxWidth", this.resizeWidth);
                //$resizableRight.resizable("option", "maxWidth", this.resizeWidthRight);
            }
        };

        $resizable.resizable({
            //containment: 'parent',
            //snap: "#video-container", snapMode: "inner",
            aspectRatio: false,
            handles: "se",
            minHeight: 500,
            minWidth: 500,
            maxHeight: 670,
            maxWidth: ()=>{
                return percent = ($(window).width()/100) * 48;
                //console.log("percentpixel: " + percent);
            }
        });   

        $resizableRight.resizable({
            //containment: 'parent',
            //snap: "#snap-container", snapMode: "inner",
            handles: "se",
            minHeight: 500,
            minWidth: 500,
            maxHeight: 670,
            maxWidth: ()=>{
                return percent = ($(window).width()/100) * 48;
                //console.log("percentpixel: " + percent);
            }      
        });  

        $(".ui-resizable-sx").mousedown(() => {
            console.log("resizable clicked");
            this.checkWidth();
            $resizable.css("width",$('.resizable').parent().css("width")-20);
            $resizableRight.css("width",$('.resizable-right').parent().css("width")-20); 

            /*
            $resizable.resizable("option", "maxHeight", this.resizeHeight);
            $resizable.resizable("option", "maxWidth", this.resizeWidth);
            $resizableRight.resizable("option", "maxHeight", this.resizeHeightRight);
            $resizableRight.resizable("option", "maxWidth", this.resizeWidthRight);
            */
        });
    }
};

