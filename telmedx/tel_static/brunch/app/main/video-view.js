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

  currentRotation: 0,

  init(el) {
    this.$el = $(el);

    if (this.$el.length) {
      this.bindUiActions();
      this.getFrame();
    }
  },

  iePolyfill: function () {
    // IE 8 Fix for IndexOf
    if (!Array.prototype.indexOf) {
      Array.prototype.indexOf = function (elt /*, from*/) {
        let len = this.length >>> 0;
        let from = Number(arguments[1]) || 0;

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

  _initPanzoom($section) {
    return $section.panzoom({
      exponential: false,
      $zoomIn: this.$section.find('.zoom-in'),
      $zoomOut: this.$section.find('.zoom-out'),
      $zoomRange: this.$section.find('.zoom-range'),
      $reset: this.$section.find('.reset')
    });
  },

  _initVideoContainer(_this) {
    $('#flash-toggle').click(function () {
      if (_this.flashToggeling || _this.frontCamera || _this.cameraToggeling) {
        return;
      }

      _this.toggleFlash();
      if (_this.isFlashOn) {
        _this.flashOff();
      } else {
        _this.flashOn();
      }
    });

    $('#camera-toggle').click(function () {
      if (_this.cameraToggeling) {
        console.log('I\'m toggleing');
        return;
      }

      _this.flashOff();
      _this.toggleCamera();
      if (!_this.frontCamera) {
        // $('#camera-toggle div:not('#camera-front-icon')').hide();
        $('#flash-toggle').addClass('disabled');
      } else {
        // $('#camera-toggle div:not('#camera-back-icon')').hide();
        $('#flash-toggle').removeClass('disabled');
      }
    });

    const $myModal = $('#myModal');
    const $hollywood = $('#hollywood');

    $myModal.bind('hidden.bs.modal', function () {
      $('html').css('margin-right', '0px');
    });

    $myModal.bind('show.bs.modal', function () {
      $('html').css('margin-right', '-15px');
    });

    $('#rotate-right').click(function () {
      let angle = ($hollywood.data('angle') + 90) || 90;
      $hollywood.css({ transform: `rotate(${angle}deg)` });
      $hollywood.data('angle', angle);

      // set global rotation value
      _this.currentRotation = angle;
      console.log('angle: ' + _this.currentRotation);
    });

    $('#rotate-left').click(function () {
      let angle = ($hollywood.data('angle') - 90) || -90;
      $hollywood.css({ transform: `rotate(${angle}deg)` });
      $hollywood.data('angle', angle);

      // set global rotation value
      _this.currentRotation = angle;
      console.log('angle: ' + _this.currentRotation);
    });

    $('#capture-button').click(function () {
      _this.takeSnapshotClicked();
    });

    $('#delete-snapshot').click(function () {
      _this.deleteSnapshot();
    });

    this.canvasSupport = this.isCanvasSupported();
    const $stream = $('#stream');

    if (!this.canvasSupport) {
      $('#c').remove();
      $stream.html(`<img id="hollywood" src="/static/img/controls/spinner.gif" />`);
    } else {
      this.canvas = document.getElementById('video-canvas');
      this.ctx = this.canvas.getContext('2d');
      this.canvas2 = document.getElementById('b');
      this.ctx2 = this.canvas2.getContext('2d');
    }

    $stream.css('overflow', 'hidden');
    if ($('html').hasClass('lt-ie9')) {
      $('#rotate-buttons').css('visibility', 'hidden');
      $('#zoom-controls').css('visibility', 'hidden');
    }
  },

  _initSnapshotContainers(_this) {
    $('#open-editor').click(function () {
      const $editSnapshot = $('#editSnapshot');
      const $drawingLayer = $('#drawing-layer');

      setTimeout(function () {
        $editSnapshot.removeClass('hundo');
        $editSnapshot.attr('src', $('#activeSnapshot').attr('src'));

        const marginleft = ($editSnapshot.parent('.modal-body').innerWidth() -
          $editSnapshot.innerWidth()) / 2;
        $editSnapshot.css('margin-left', marginleft);

        $drawingLayer.css('marginleft', marginleft);
        $drawingLayer.css('height', $editSnapshot.height());
        $drawingLayer.css('width', $editSnapshot.width());
      }, 1000);
    });

    $(window).resize(function () {
      _this.sizePreview();
    });

    this.sizePreview();

    $('div').on('click', '.closeDiv', function () {
      let snapDeleteID = $(this).attr('id');
      let snapID = snapDeleteID.replace('delete-', '');
      $('#' + snapID).remove();
      $('#' + snapDeleteID).remove();
      $('.' + 'container-' + snapID).remove();
      console.log('item deleted');
    });

    // Bind pastSnapshots for future snapshots
    $('#pastSnapshots').on('click', '.snap-item', function (ev) {
      // Snapshot id
      const sid = $(ev.target).data('sid');
      _this.showSnapshot(sid);
    });

    $('#activeSnapshot').dblclick(function () {
      // calls panzoom zoom function click
      $('#capture-snaper').first().find('.zoom-in').click();
    });
  },

  bindUiActions() {
    const _this = this;
    this.$section = $('#capture-snaper').first();
    this.deviceName = $('#deviceName').data('name');

    // Initialize Panzoom container
    this._initPanzoom(this.$section.find('.panzoom'));

    // Initialize all elements in the streaming video container
    this._initVideoContainer(_this);

    // Initialize snapshot containers
    this._initSnapshotContainers(_this);

    this.bindResizeEvents();
  },

  isCanvasSupported() {
    return false;
    const elem = document.createElement('canvas');
    return !!(elem.getContext && elem.getContext('2d'));
  },

  inviteClicked() {
    $.post('/ttux/invite');
  },

  // adds border to snapshot
  select(id) {
    $('.snapshot').css('border', 'none');
    $('#' + id).css('border', '4px solid');
    this.$section.find('.panzoom').panzoom('reset');
  },

  showSnapshot(id) {
    const $selected = $('#' + id);
    const $activeSnapshot = $('#activeSnapshot');
    $activeSnapshot.attr('src', $selected.attr('src'));
    $activeSnapshot.css({ transform: `rotate(${$selected.data('rotate')}deg)` });
    this.select(id);
  },

  deleteSnapshot(id) {
    console.log('Snapshot deleted');
  },

  makeid() {
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let text = '';

    for (let i = 0; i < 15; i++) {
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    }

    return text;
  },

  toggleFlash() {
    const _this = this;
    this.flashToggeling = true;

    $.ajax({
      url: '/ttux/flashlight/' + this.deviceName
    }).done(function (data) {
      console.log(data);
      _this.flashToggeling = false;
      if (data.status === 'on') {
        _this.flashOn();
      } else if (data.status === 'off') {
        _this.flashOff();
      } else {
        console.log('Something went wrong with the flash');
      }
    });
  },

  takeSnapshotClicked() {
    const _this = this;
    let ie = !!$('html').hasClass('lt-ie9');

    $.post('/ttux/snapshot/' + this.deviceName, { ie: ie }, function (data) {
      let dataUri;
      const $activeSnapshot = $('#activeSnapshot');

      if (ie) {
        dataUri = '/ttux/ie-snapshot/' + _this.deviceName + '/' + _this.makeid();
      } else {
        dataUri = 'data:image/jpeg;base64,' + data.image;
      }

      if (_this.canvasSupport && !ie) {
        const image = new Image();
        image.src = dataUri;
        image.onload = function () {
          let cw = image.width;
          let ch = image.height;
          let cx = 0;
          let cy = 0;
          let ratio = cw / ch;

          //Calculate new canvas size and x/y coorditates for image
          switch (_this.rotate) {
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

          //Rotate image
          _this.canvas2.setAttribute('width', cw);
          _this.canvas2.setAttribute('height', ch);
          _this.ctx2.rotate(rotate * Math.PI / 180);
          _this.ctx2.drawImage(image, cx, cy);//Display Image in Canvas
          dataUri = _this.canvas2.toDataURL();

          $activeSnapshot.attr('src', dataUri);
          $activeSnapshot.css('margin-left', ($('#snapshots').innerWidth() -
            $('#activeSnapshot').innerWidth()) / 2);

          const id = 'snapshot-' + new Date().getTime().toString();
          if (_this.rotate === 90 || _this.rotate === 270) {
            smwidth = 45;
            smheight = 45 * ratio;
          } else {
            smwidth = 45 * ratio;
            smheight = 45;
          }

          let imageElement = $.parseHTML(`<img class="snapshot-item snapshot" 
             id="${id}" src="${dataUri}" width="${String(smwidth)}"
             height="${String(smheight)}" onclick="window.parent.showSnapshot('${id}')">`);

          let container = document.createElement('div');

          // maybe make class unique, or an id via the const id above
          container.setAttribute('class', 'container-' + id);
          container.setAttribute('style', 'display: inline-flex;');

          // create delete icon
          let div = document.createElement('div');
          div.setAttribute('class', 'closeDiv');
          div.setAttribute('id', 'delete-' + id);

          const $container = $(container);
          $container.append(imageElement);
          $container.append(div);

          $('#pastSnapshots').append($container);

          _this.select(id);
        };
      } else {
        // Canvas should not be called, so this code is executed
        const id = 'snapshot-' + new Date().getTime().toString();
        let currentRotation = _this.currentRotation;
        console.log('current: ' + currentRotation);

        $activeSnapshot.attr('src', dataUri);
        $activeSnapshot.css({ transform: `rotate(${currentRotation}deg)` });
        _this.$section.find('.panzoom').panzoom('reset');

        let imageElement = $.parseHTML(`<img data-sid='${id}' 
            class='snap-item snapshot' id='${id}' src='${dataUri}' 
            width='75' height='50' data-rotate='${currentRotation}'>`);

        let container = document.createElement('div');

        // maybe make class unique, or an id via the const id above
        container.setAttribute('class', 'container-' + id);
        container.setAttribute('style', 'display: inline-flex;');

        // Uncomment this line to set rotation on snapshot panel
        //container.style.transform = 'rotate(' + currentRotation + 'deg)';

        // create delete icon
        let div = document.createElement('div');
        div.setAttribute('class', 'closeDiv');
        div.setAttribute('id', 'delete-' + id);

        const $container = $(container);
        $container.append(imageElement);
        $container.append(div);

        $('#pastSnapshots').append($container);

        _this.select(id);
      }
    });
  },

  /**
   * Contains the main logic for requesting and processing command and image
   * frames requested from the server.
   */
  getFrame() {
    const _this = this;

    $.ajax({
      url: `/ttux/lastFrame/${this.deviceName}/${this.lastFrame}`
    }).done(function (msg) {
      let fnumber = msg.substring(0, 8);
      let beginImgData = 8;

      if (msg.substring(0, 2) === '!!') {
        let beginEnd = msg.indexOf('!!', 2);
        let control = $.parseJSON(msg.substring(2, parseInt(beginEnd, 10)));
        _this.controlOutput = control;

        if (control.command === 'update_controls' && !$('html').hasClass('lt-ie9')) {
          if (control.parameters.indexOf('flash') !== -1) {
            $('#flash-toggle').show();
          }

          if (control.parameters.indexOf('flip') !== -1) {
            $('#camera-toggle').show();
          }
        }

        fnumber = msg.substring(parseInt(beginEnd, 10) + 2, parseInt(beginEnd, 10) + 10);
        beginImgData = parseInt(beginEnd, 10) + 10;
      }

      _this.lastFrame = fnumber;
      if (msg.substring(8).length > 0) {
        let videoSrc = 'data:image/jpg;base64,' + msg.substring(beginImgData);

        if (_this.canvasSupport) {
          const image = new Image();
          image.src = videoSrc;

          image.onload = function () {
            let cw = image.width;
            let ch = image.height;
            let cx = 0;
            let cy = 0;

            // Calculate new canvas size and x/y coorditates for image
            switch (_this.rotate) {
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
            _this.canvas.setAttribute('width', cw);
            _this.canvas.setAttribute('height', ch);
            _this.ctx.rotate(_this.rotate * Math.PI / 180);

            //Scales the image down if it won't fit in the box
            if (cw > _this.streamBox.innerWidth()) {
              _this.ctx.scale(_this.streamBox.innerWidth() / cw, _this.streamBox.innerWidth() / cw);

              // streamBox.css('height',ch*streamBox.innerWidth()/cw+'px');
            }

            _this.ctx.drawImage(image, cx, cy);//Display Image in Canvas
          };
        } else { //If canvas is not supported display in img tag
          $('#hollywood').attr('src', videoSrc);
        }

        let now = new Date();
        let min = Math.floor((now - _this.startTime) / 1000);
        let sec = (now - _this.startTime) % 1000;

        $('#stream_status').html(min + '.' + sec + ' f: ' + _this.fCounter);
        _this.fCounter++; //Adds to frame couter
      }

      _this.getFrame(); //Let the function call itself
    });

    //.error(function (msg) {
    // console.log('got error');
    // setTimeout('frameOne_jq()', 500);
    // });
  },

  toggleCamera() {
    const _this = this;
    this.cameraToggeling = true;

    $.ajax({
      url: '/ttux/flipcamera/' + this.deviceName
    }).done(function (data) {
      _this.cameraToggeling = false;
      if (data.status === 'front') {
        _this.frontCamera = true;
        $('#camera-front-icon').show();
        $('#flash-toggle').addClass('disabled');

      } else if (data.status === 'back') {
        _this.frontCamera = false;
        $('#camera-back-icon').show();
        $('#flash-toggle').removeClass('disabled');
      }
    });
  },

  sizePreview() {
    if ($('body').innerWidth() > 992) {
      let snaperh = $(window).height() - 110 - 30;
      $('#capture-snaper').css('height', snaperh);
      $('#cap-body').css('height', snaperh - $('#cap-head').outerHeight());
    } else {
      $('#cap-body').css('height', '100%');
    }
  },

  flashOn() {
    this.isFlashOn = true;
    const $flashToggle = $('#flash-toggle');
    $flashToggle.html('<img style="height: 50px;" src="/static/img/controls/open103off.png">');
    $flashToggle.removeClass('active');
  },

  flashOff() {
    this.isFlashOn = false;
    const $flashToggle = $('#flash-toggle');
    $flashToggle.html('<img style="height: 50px;" src="/static/img/controls/open103.png">');
    $flashToggle.removeClass('active');
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
      this.resizeWidth = $window.width() - 30;
      this.resizeWidthRight = $window.width() - 30;
    } else {
      this.resizeWidth = 885;
      this.resizeWidthRight = 892.5;
    }
  },

  locateStream() {
    /*
     * This function is to allow or disable resizing of the container before stream has loaded in
    */

    // see if stream elementExists
    // if it does not, disable resizing?
    const $elementExists = $('#hollywood');
    if (!$elementExists) {
      console.log('Cannot find hollywood');
    } else {
      console.log('hollywood exists');
    }
  },

  /**
   * Bindings to adjust layout based on window size.
   */
  bindResizeEvents() {
    // Window resizing adjustments
    const $resizable = $('.resizable');
    const $resizableRight = $('.resizable-right');

    const $videoContainer = $('#video-container');
    const $snapContainer = $('#snap-container');

    //this.checkWidth();
    this.locateStream();

    $(window).resize(function () {
      //this.checkWidth();
      console.log('window resize here');

      // sets snapContainer width to percentage of screen
      let calc = ($(window).width() / 100) * 40;
      $snapContainer.css('width', calc);
      $snapContainer.css('width', $('#first-right').width());

      // sets maxWidth based on screen percentage
      $resizableRight.resizable('option', 'maxWidth', calc);

      setOffset();
      checkoverlap();
    });

    /**
     * Checks if videoStream container and Snapshot viewer are overlapping
     */
    function checkoverlap() {
      let positionLeft = $resizable.offset().left + $resizable.width();
      let positionRight = $resizableRight.offset().left;

      if (positionLeft > positionRight) {
        // overlapping = TRUE
        console.log('overlapping!');
      }
    }

    function setOffset() {
      // sets snapshot resizable, to the top left corner of its div, upon window resize
      let positionRight = $resizableRight.offset().left;
      let positionRightParent = $('#first-right').offset();

      $resizableRight.offset({ top: positionRightParent.top, left: positionRightParent.left });
    }

    $resizableRight.resizable({
      //containment: '#first-right',
      disabled: true,
      snap: '#first-right', snapMode: 'inner',
      aspectRatio: false,
      handles: 'sw',
      minHeight: 400,
      minWidth: 400,
      maxHeight: 670,
      resize: function (event, ui) {
        // sets maxWidth based on screen percentage
        let calc;
        console.log('CALCpercentpixel: ' + calc);

        //if column layout, set percentage to 94
        if ($(window).width() < 950) {
          calc = ($(window).width() / 100) * 94;
          $resizableRight.resizable('option', 'maxWidth', calc);

        } else {
          calc = ($(window).width() / 100) * 40;
          $resizableRight.resizable('option', 'maxWidth', calc);
        }
      }
    }).on('resize', function (e) {
      e.stopPropagation();
    });
  },
};

