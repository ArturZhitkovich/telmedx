// User Interface Elements

		
		function selectLight_On(deviceName) {
			console.log("selectLight_On() selected");
			jQuery.get("/ttux/01/uiLightOn/" + deviceName);
		}
		
		function selectLight_Off(deviceName) {
			console.log("selectLight_Off() selected");
			jQuery.get("/ttux/01/uiLightOff/" + deviceName);
		}


		function saveCurrentImage() {
			console.log("saveCurrentImage() selected");
		}

		function printCurrentImage() {
			console.log("printCurrentImage() selected");
		}

		function rotateImage() {
			console.log("rotateImage() selected");
		}

		function inviteClicked() {
			jQuery.post("/ttux/invite");
		}
		
		function select(id) {
			$(".snapshot").css("border", "none");
			$("#" + id).css("border", "4px solid");
		}
		
		function showSnapshot(id) {
			var selected = $("#" + id);
			
			$("#activeSnapshot").attr("src", selected.attr("src"));
			select(id);
		}
		
		function takeSnapshotClicked(deviceName) {
			$.post("/ttux/01/snapshot/" + deviceName, null, function(data) {
				dataUri = "data:image/jpeg;base64," + data.image;
				$("#activeSnapshot").attr("src", dataUri);
				
				var id = "snapshot-" + new Date().getTime().toString();
				var imageElement = "<img class=\"snapshot\" id=\"" + id + "\" src=\"" + dataUri + "\" width=\"75\" height=\"50\" onclick=\"window.parent.showSnapshot('" + id + "')\"> "
				
				$("#pastSnapshots").append(imageElement);
				
				select(id);
			});
			
			$("#activeSnapshot").attr("src", "/static/img/spinner.gif")
		}


		var ff=0;
		var lastFrame = 0;
		var fCounter = 0;
		var startTime = new Date();

		// jquery video driver
		function frameOne_jq(deviceName)
		{
			var r = $.ajax({
				url: "/ttux/01/lastFrame/" + deviceName + "/" + lastFrame
			});
			
			r.done( function(msg) {
				var fnumber = msg.substring(0,8);
				lastFrame = fnumber;

				if (msg.substring(8).length > 0) {
	            			videoSrc = "data:image/jpg;base64," + msg.substring(8);
	            			$("#hollywood").attr("src", videoSrc);
	            			var now = new Date();
	            			var min = Math.floor( ( (now - startTime)/1000) );
	            			var sec = (now - startTime)%1000;
	            			$("#stream_status").html(deviceName + ": Connected:" + min + "." + sec + " f:" + fCounter);
	            			fCounter++;
				}
	            
				//console.log("got frame: " + fnumber);
				//setTimeout("frameOne_jq()", 100);
				frameOne_jq(deviceName);
			});

			// error handler, wait 1/2 second
			r.error( function(msg) {
				console.log("got error");
				//setTimeout("frameOne_jq(" + deviceName + ")", 500);
				setTimeout( function() { frameOne_jq( deviceName ) }, 5000);
			});

		}
		
		var deviceLightState = "off"; // keep track of the current device light state
		
		function checkDeviceState(deviceName)
		{
			console.log("checking state for device: " + deviceName);		
			
			var r = $.ajax({
				dataType: "json",
				url: "/ttux/01/getDevState/" + deviceName,
			});
			
			// success handler
			r.done( function(msg) {
				deviceLightState =  msg['light_state']; // remember the state
				
				$("#light_state").html( msg['light_state'] );
				if ( msg['light_state'] == "on" ) {
					console.log("light is on");
					//$("#lightSel").value="On";
					//$('[name=lightSel]').attr('checked', true);
					//document.getElementById("lightSelOn").checked = true;
					//document.getElementById("lightSelOff").checked = false
				} else
				{
					console.log("light is off");
					//$("#lightSel").value="Off";
					//$('input[value="Off"][name="lightSel"]');
					//$('[name=lightSel]').attr('checked', true);
					//document.getElementById("lightSelOff").checked = true;
				}
				setTimeout( function() { checkDeviceState( deviceName ) }, 1000);
			});

			// error handler
			// TODO x.error is deprecated in jQuery 1.8, need to change to x.fail()
			// see http://api.jquery.com/jQuery.getJSON/
			r.error( function(msg) {
				console.log("got device state error");
				//setTimeout("checkDeviceState(" + deviceName + ")", 5000);
				setTimeout( function() { checkDeviceState( deviceName ) }, 5000);
			});
			
			console.log("exit checking state for device");
		}		

		function changeLightState(deviceName) {
			console.log("changeLightState() selected, current state: " + deviceLightState );
			if ( "off" == deviceLightState) {
				jQuery.get("/ttux/01/uiLightOn/" + deviceName);
			} else {
				jQuery.get("/ttux/01/uiLightOff/" + deviceName);
			}
		}