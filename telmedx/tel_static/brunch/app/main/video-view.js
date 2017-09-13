const $ = require('jquery'),
    panzoom = require('jquery.panzoom');


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
        const $section = $('#capture-snaper').first();

        this.deviceName = $("#deviceName").data('name');

        $section.find('.panzoom').panzoom({
            $zoomIn: $section.find(".zoom-in"),
            $zoomOut: $section.find(".zoom-out"),
            $zoomRange: $section.find(".zoom-range"),
            $reset: $section.find(".reset")
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

        $("#flash-toggle").css("width", $("#flash-toggle").outerWidth());

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
            context.rotate = context.rotate + 90;
            if (context.rotate === 360) {
                context.rotate = 0;
            }
        });

        $("#rotate-left").click(function () {
            context.rotate = context.rotate - 90;
            if (context.rotate === -90) {
                context.rotate = 270;
            }
        });

        $("#capture-button").click(function () {
            context.takeSnapshotClicked();
        });

        this.canvasSupport = this.isCanvasSupported();
        const $stream = $('#stream');
        if (!this.canvasSupport) {
            $("#c").remove();
            $stream.html('<img id="hollywood" src="/static/img/controls/spinner.gif" />');
        } else {
            this.canvas = document.getElementById("c");
            this.ctx = canvas.getContext('2d');
            this.canvas2 = document.getElementById("b");
            this.ctx2 = canvas2.getContext('2d');
        }

        $stream.css("overflow", "hidden");
        if ($('html').hasClass('lt-ie9')) {
            $("#rotate-buttons").css("visibility", "hidden");
            $("#zoom-controls").css("visibility", "hidden");
        }

        //Ask for the first frame
    },

    isCanvasSupported() {
        return false;
        const elem = document.createElement('canvas');
        return !!(elem.getContext && elem.getContext('2d'));
    },

    inviteClicked() {
        $.post("/ttux/invite");
    },

    select(id) {
        $(".snapshot").css("border", "none");
        $("#" + id).css("border", "4px solid");
        $section.find('.panzoom').panzoom("reset");
    },

    showSnapshot(id) {
        const selected = $("#" + id);
        $("#activeSnapshot").attr("src", selected.attr("src"));
        select(id);
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
            console.log(dataUri);

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
                    console.log(dataUri);

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

                    const imageElement = "<img class=\"snapshot\" id=\"" + id + "\" src=\"" + dataUri + "\" width=\"" + String(smwidth) + "\" height=\"" + String(smheight) + "\" onclick=\"window.parent.showSnapshot('" + id + "')\"> ";

                    $("#pastSnapshots").append(imageElement);

                    select(id);
                };
            } else {
                $("#activeSnapshot").attr("src", dataUri);
                $section.find('.panzoom').panzoom("reset");
                const id = "snapshot-" + new Date().getTime().toString(),
                    imageElement = "<img class=\"snapshot\" id=\"" + id + "\" src=\"" + dataUri + "\" width=\"75\" height=\"50\" onclick=\"window.parent.showSnapshot('" + id + "')\"> ";

                $("#pastSnapshots").append(imageElement);

                select(id);
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
            console.log(`last frame ${context.lastFrame}`);

            if (msg.substring(8).length > 0) {
                let videoSrc = "data:image/jpg;base64," + msg.substring(begin_img_data);

                if (context.canvasSupport) {
                    const image = new Image();
                    image.src = videoSrc;

                    image.onload = function () {
                        let cw = image.width, ch = image.height, cx = 0, cy = 0;
                        // Calculate new canvas size and x/y coorditates for image
                        switch (rotate) {
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
                        context.ctx.rotate(rotate * Math.PI / 180);

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
        $("#flash-toggle").html('<img style="height: 50px;" src="/static/img/controls/open103off.png">');
        $("#flash-toggle").removeClass('active');
    },

    flashOff() {
        this.isFlashOn = false;
        $("#flash-toggle").html('<img style="height: 50px;" src="/static/img/controls/open103.png">');
        $("#flash-toggle").removeClass('active');
    }
};

