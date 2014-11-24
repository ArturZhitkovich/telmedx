//Frame counter & UI
var ff=0;
var lastFrame = 0;
var fCounter = 0;
var startTime = new Date();

//video feed rotation
var rotate = 90;//Default Rotation
var ctx;
var canvas;

//Stream box & Device
var streamBox;
var deviceName;

//large image rotation
var ctx2;
var canvas2;

//Canvas support
var canvasSupport; //true or false, defines if we should use canvas or img

//Sketchpad
var sketchpad;

//Flash
var flashToggeling = false;

//Camera
var frontCamera = false;
var cameraToggeling = false;

//Caputred Image Viewer
var $section;

function isCanvasSupported(){
  var elem = document.createElement('canvas');
  return !!(elem.getContext && elem.getContext('2d'));
}
function inviteClicked() {
  jQuery.post("/ttux/invite");
}
  
function select(id) {
  $(".snapshot").css("border", "none");
  $("#" + id).css("border", "4px solid");
  $section.find('.panzoom').panzoom("reset");
}

function showSnapshot(id) {
  var selected = $("#" + id);
  $("#activeSnapshot").attr("src", selected.attr("src"));
  select(id);
}

function takeSnapshotClicked() {
  $.post("/ttux/snapshot/"+deviceName, null, function(data) {
    var dataUri = "data:image/jpeg;base64," + data.image;
    if( canvasSupport ){
      var image = new Image();
      image.src = dataUri;
      image.onload = function() {
        var cw = image.width, ch = image.height, cx = 0, cy = 0; ratio = cw/ch;
        //Calculate new canvas size and x/y coorditates for image
        switch(rotate){
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
        console.log(rotate);
        
        //Rotate image            
        canvas2.setAttribute('width', cw);
        canvas2.setAttribute('height', ch);
        ctx2.rotate(rotate * Math.PI / 180);
        ctx2.drawImage(image, cx, cy);//Display Image in Canvas
        dataUri = canvas2.toDataURL();
        console.log(dataUri);
        $("#activeSnapshot").attr("src", dataUri);
        //Center the image
        $("#activeSnapshot").css("margin-left", ($("#snapshots").innerWidth()-$("#activeSnapshot").innerWidth())/2 );
        var id = "snapshot-" + new Date().getTime().toString();
        if( rotate == 90 || rotate == 270) {
          smwidth = 45;
          smheight = 45* ratio;
        }else{
          smwidth = 45*ratio;
          smheight = 45;
        }
        var imageElement = "<img class=\"snapshot\" id=\"" + id + "\" src=\"" + dataUri + "\" width=\""+String(smwidth)+"\" height=\""+String(smheight)+"\" onclick=\"window.parent.showSnapshot('" + id + "')\"> ";
        
        $("#pastSnapshots").append(imageElement);
        
        select(id);
      };//End image.onload
    }else
    {
      $("#activeSnapshot").attr("src", dataUri);
      $section.find('.panzoom').panzoom("reset");
      var id = "snapshot-" + new Date().getTime().toString();
      var imageElement = "<img class=\"snapshot\" id=\"" + id + "\" src=\"" + dataUri + "\" width=\"75\" height=\"50\" onclick=\"window.parent.showSnapshot('" + id + "')\"> ";
      
      $("#pastSnapshots").append(imageElement);
      
      select(id);
    }
  });
}
function flashOn(){
  $("#flash-toggle").addClass('active');
  $("#flash-toggle").html('<img style="height: 50px;" src="/static/img/controls/open103off.png">');
}
function flashOff(){
  $("#flash-toggle").removeClass('active');
  $("#flash-toggle").html('<img style="height: 50px;" src="/static/img/controls/open103.png">');
}
function toggle_jq(){
  flashToggeling = true;
  var r = $.ajax({
    url: "/ttux/flashlight/"+deviceName
  });

  r.done( function(data){
    console.log(data);
    flashToggeling = false;
    if( data.status == 'on' ){
      flashOn();
    }else if( data.status == 'off'){
      flashOff();
    }else{
      console.log("Something went wrong with the flash");
    }
  });
}
function toggle_camera_jq(){
  cameraToggeling = true;

  var r = $.ajax({
    url: "/ttux/flipcamera/"+deviceName
  });

  r.done( function(data){
    console.log(data);
    cameraToggeling = false;
    if( data.status == 'front' ){
      frontCamera = true;
      $("#camera-toggle div:not('#camera-front-icon')").hide();
      $("#camera-front-icon").show();
      $("#flash-toggle").addClass('disabled');

    }else if (data.status == 'back'){
      frontCamera = false;
      $("#camera-toggle div:not('#camera-back-icon')").hide();
      $("#camera-back-icon").show();
      $("#flash-toggle").removeClass('disabled');

    }else{
      console.log("Something went wrong with the camera");
    }
  });
}
function frameOne_jq(){

  var r = $.ajax({//Go get frame
    url: "/ttux/lastFrame/"+deviceName+"/" + lastFrame
  });
  
  r.done( function(msg) {
    // console.log(msg.substring(0,15));
    var fnumber = msg.substring(0,8);
    var begin_img_data = 8;
    if( msg.substring(0,2) == '!!'){
      begin_end = msg.indexOf('!!', 2);
      control = $.parseJSON( msg.substring(2, parseInt( begin_end, 10 )   ) );
      if( control.command == 'update_controls' ){
        if(control.parameters.indexOf('flash') != -1){
          $("#flash-toggle").show();
        }
        if(control.parameters.indexOf('flip') != -1){
          $("#camera-toggle").show();
        }
      }
      fnumber = msg.substring( parseInt(begin_end, 10)+ 2 ,parseInt(begin_end, 10)+ 10);
      begin_img_data = parseInt(begin_end, 10)+ 10;
    }
    
    lastFrame = fnumber;
    if (msg.substring(8).length > 0) {
      videoSrc = "data:image/jpg;base64," + msg.substring(begin_img_data);
      if( canvasSupport ){
        var image = new Image();
        image.src = videoSrc;
        image.onload = function() {
          var cw = image.width, ch = image.height, cx = 0, cy = 0;
          //Calculate new canvas size and x/y coorditates for image
          switch(rotate){
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
          canvas.setAttribute('width', cw);
          canvas.setAttribute('height', ch);
          ctx.rotate(rotate * Math.PI / 180);
          if( cw > streamBox.innerWidth() )//Scales the image down if it won't fit in the box
          {
            ctx.scale(streamBox.innerWidth()/cw,streamBox.innerWidth()/cw);
            // streamBox.css("height",ch*streamBox.innerWidth()/cw+"px");
          }
          ctx.drawImage(image, cx, cy);//Display Image in Canvas
        };//End image.onload
      }else{ //If canvas is not supported display in img tag
        $("#hollywood").attr('src',videoSrc);
      }
      var now = new Date();
      var min = Math.floor( (now - startTime)/1000 );
      var sec = (now - startTime)%1000;
      
      $("#stream_status").html(min + "." + sec + " f: " + fCounter );
      fCounter++; //Adds to frame couter
    }
      frameOne_jq(); //Let the function call itself
  });

  // error handler, wait 1/2 second
  r.error( function(msg) {
    console.log("got error");
    setTimeout("frameOne_jq()", 500);
  });

}
// (function() {

// })();
function sizePreview(){
  if( $("body").innerWidth() > 992){
    var snaperh = $(window).height() -110 -30;
    $("#capture-snaper").css("height",snaperh);
    $("#cap-body").css("height",snaperh - $("#cap-head").outerHeight());
  }else{
    $("#cap-body").css("height","400px");
  }
}
$(document).ready(function()
{
  $section = $('#capture-snaper').first();
  $section.find('.panzoom').panzoom({
    $zoomIn: $section.find(".zoom-in"),
    $zoomOut: $section.find(".zoom-out"),
    $zoomRange: $section.find(".zoom-range"),
    $reset: $section.find(".reset")
  });
  deviceName = $("#deviceName").data('name');
  $("#open-editor").click(function(){
    console.log("Clicked");
    setTimeout( function(){
      $('#editSnapshot').removeClass('hundo');
      $("#editSnapshot").attr('src',$("#activeSnapshot").attr('src'));
      var marginleft= ( $("#editSnapshot").parent(".modal-body").innerWidth() - $("#editSnapshot").innerWidth())/2;
      $("#editSnapshot").css("margin-left",  marginleft );
      $("#drawing-layer").css("marginleft", marginleft );
      $("#drawing-layer").css("height", $("#editSnapshot").height());
      $("#drawing-layer").css("width", $("#editSnapshot").width());
    }, 1000);
  });
  $("#flash-toggle").click(function(){
    if( flashToggeling || frontCamera || cameraToggeling){
      return;
    }
    toggle_jq();
    if( $(this).hasClass('active') ){
      flashOff();
    }else{
      flashOn();
    }
  });
  $("#flash-toggle").css("width",$("#flash-toggle").outerWidth());
  // $("#capture-snaper").css("border","1px solid red");
  $(window).resize(function(){
    sizePreview();
  });
  sizePreview();
  // $("#drawing-layer").attr("height",$("#activeSnapshot").innerHeight());
  // $("#drawing-layer").attr("width",$("#activeSnapshot").innerWidth());

    // sketchpad = Raphael.sketchpad("drawing-layer", {
    //   width: 400,
    //   height: 400,
    //   editing: true
    // });

  // $("[data-tool='marker'],[data-tool='eraser'] ").attr('href',document.URL+"#drawing-layer")
  // $('#drawing-layer').sketch({defaultColor: "#ff0"});

  // $("#activeSnapshot").height(snaperh - $("#cap-head").outerHeight()-30)
  var previous_camera_toggle_state;
  $("#camera-toggle").hover(function(){
    previous_camera_toggle_state = $(this).find('div:visible').attr('id');
    $(this).find('div').not('#camera-toggle-icon').hide();
    $(this).find('#camera-toggle-icon').show();
  }, function(){
    $(this).find('div').hide();
    $(this).find('#'+previous_camera_toggle_state).show();
  });
  $("#camera-toggle div:not('#camera-back-icon')").hide();
  $("#camera-toggle").click(function(){
    if( cameraToggeling ){
      console.log('I\'m toggleing');
      return;
    }
    flashOff();
    toggle_camera_jq();
    if( ! frontCamera ){
      $("#camera-toggle div:not('#camera-front-icon')").hide();
      $("#flash-toggle").addClass('disabled');
    }else{
      $("#camera-toggle div:not('#camera-back-icon')").hide();
      $("#flash-toggle").removeClass('disabled');

    }
  });


  $('#myModal').bind('hidden.bs.modal', function () {
    $("html").css("margin-right", "0px");
  });
  $('#myModal').bind('show.bs.modal', function () {
    $("html").css("margin-right", "-15px");
  });
  $("#rotate-right").click(function(){
    rotate = rotate+90;
    if( rotate == 360){
      rotate = 0;
    }
  });
  $("#rotate-left").click(function(){
    rotate = rotate-90;
    if( rotate == -90){
      rotate = 270;
    }
  });
  $("#capture-button").click(function(){
    takeSnapshotClicked();
  });

  canvasSupport = isCanvasSupported();
  if ( ! canvasSupport ){
    $("#c").remove();
    $("#stream").html('<img id="hollywood" src="/static/img/controls/spinner.gif" ></img>');
  }else{
    canvas = document.getElementById("c");
    ctx = canvas.getContext('2d');
    canvas2 = document.getElementById("b");
    ctx2 = canvas2.getContext('2d');
  }
  streamBox = $("#stream");
  streamBox.css("overflow","hidden");

  //Ask for the first frame
  frameOne_jq();
});