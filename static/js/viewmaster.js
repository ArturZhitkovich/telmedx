// User Interface Elements

		function imageQ_Good() {
			console.log("imageQ_Good() selected");
		}

		function imageQ_Bad() {
			console.log("imageQ_Bad() selected");
		}
		
		function imageQ_Ugly() {
			console.log("imageQ_Ugly() selected");
		}		

		function selectCam_Back() {
			console.log("selectCam_Back() selected");
		}
		
		function selectCam_Front() {
			console.log("selectCam_Front() selected");
		}
		
		function selectLight_On() {
			console.log("selectLight_On() selected");
		}
		
		function selectLight_Off() {
			console.log("selectLight_Off() selected");
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
				setTimeout("frameOne_jq(" + deviceName + ")", 500);
			});

		}		
