#!/usr/bin/perl
# stream test images to ttux server via http put
# simulate iphone

use HTTP::Request;
use LWP::UserAgent;

use IO::Socket;
use Time::HiRes qw(usleep ualarm gettimeofday tv_interval);
use strict;
use JSON;
use Switch;

# time tux stream test utility, send a stream of frames
# from the img directory of the format frame#.jpg
# and loop
# usage: scarryTux_http.pl server-addr port filePrefix

die "Usage: scarryTux.pl server-addr port# file.jpg OTUK\n"
  unless ( $#ARGV eq 3 );
my $serverAddress = $ARGV[0];
my $portNumber    = $ARGV[1];
my $filePrefix    = $ARGV[2];
my $OTUK          = $ARGV[3];
print "server:  $serverAddress \n";
print "port:    $portNumber \n";
print "frames:  " . "img/" . "$filePrefix" . "#" . ".jpg \n";
print "OTUK: " . $OTUK . "\n";

# make sure the first frame is there
if ( !-e "img/" . "$filePrefix" . "0" . ".jpg" ) {
	die "ERR: there are no frames with that prefix in img/ \n";
}

# send to TT server
#my $sock = new IO::Socket::INET (
#	PeerAddr => $serverAddress,
#	PeerPort => $portNumber,
#	Proto => 'udp',
#	);

#send multiple frames
my $frameSeqNo    = 0;
my $numFramesSent = 0;

my $device_profile = {
	'app_version'  => '1.00',
	'app_type'     => 'telmedx',
	'phone_number' => '123-456-7890'
};

my $phone_status = {
	'camera_state' => 'front',
	'light_state'  => 'on',
	'flash_state'  => 'on'
};

my $url = "http://$serverAddress:$portNumber/ttux/01/register/" . $OTUK . "\n";
print $url;
my $data = { 'device_profile' => $device_profile };
print to_json($data) . "\n";
my $r = new HTTP::Request 'POST', $url;
$r->header( 'content-type' => 'application/json' );
$r->content( to_json($data) );

my $SUID;
my $ua       = LWP::UserAgent->new;
my $response = $ua->request($r);
if ( $response->is_success ) {
	my $data   = from_json( $response->content );
	my $result = ${$data}[0]->{'result'};
	if ( $result eq "REGISTER_OK" ) {
		$SUID = ${$data}[0]->{'SUID'};
	}
	else {
		print $result. "\n";
		exit;
	}
}
else {
	print "did not register\n";
	exit;
}
print "SUID: " . $SUID . "\n";

while (1) {

	# read in the file and find out the size
	my $fileToSend = "img/" . $filePrefix . $frameSeqNo . ".jpg";

	#open FILE, "$fileToSend" or die "File not found: $fileToSend \n";
	if ( !open FILE, "$fileToSend" ) {

		# reset back to the first frame
		#print "** back to first frame \n";
		$frameSeqNo = 0;
		next;
	}

	my $url =
	  "http://$serverAddress:$portNumber/ttux/01/img/" . $SUID . "/img"
	  . $frameSeqNo . ".jpg";

	#print "PUT url= $url \n";

	binmode FILE;
	my $fileLength = -s $fileToSend;

   #print "sending $fileToSend size: $fileLength bytes frame# $numFramesSent\n";

	# read the image file
	my $data;
	my $numBytesRead = 0;
	$numBytesRead = read FILE, $data, $fileLength;

	# send it
	my $r = new HTTP::Request 'PUT', $url;
	$r->header( 'content-length' => $numBytesRead );
	$r->header( 'content-type'   => 'image/jpeg' );
	$r->content($data);

	my $ua       = LWP::UserAgent->new;
	my $response = $ua->request($r);
	HandleResponse( $response, $data, $numBytesRead );

	close(FILE);
	$numFramesSent++;

	#next frame
	$frameSeqNo++;
	if ( $frameSeqNo > 255 ) { $frameSeqNo = 0; }

	#print "\n\n**Next frame seq no: $frameSeqNo \n";
	# sleep(10);
	# usleep(500000); # half second
	usleep(250000);    # 1/4 second
	                   #usleep(125000); # 1/8 second
	                   #usleep(25000);

	if ( $numFramesSent % 4 == 0 ) {
		$response = SendPing();
		HandleResponse( $response, $data, $numBytesRead );
	}
}

#camera_state: “front” | ”back”,
#[ light_state: (“on”|, “off”) ],
#[ flash_state: “on” | “off” | “auto” ]
sub HandleResponse {
	my $response     = $_[0];
	my $data         = $_[1];
	my $numBytesRead = $_[2];
	if ( $response->is_success ) {
		my $decodedResponse = $response->decoded_content;
		switch ($decodedResponse) {
			case ''                { }
			case 'OK_PONG'         { print "Pong Received\n" }
			case 'OK_SNAPSHOT_REQ' { SendSnapshot( $data, $numBytesRead ) }
			case '/snapshot'       { SendSnapshot( $data, $numBytesRead ) }
			case 'OK_FRONT_CAM'    {
				print "Switch Front Cam";
				$phone_status->{'camera_state'} = 'front';
			}
			case 'OK_BACK_CAM' {
				print "Switch Back Cam";
				$phone_status->{'camera_state'} = 'back';
			}
			case 'OK_LIGHT_ON' {
				print "Switch Light On";
				$phone_status->{'light_state'} = 'on';
			}
			case 'OK_LIGHT_OFF' {
				print "Switch Light Off";
				$phone_status->{'light_state'} = 'off';
			}
			case 'OK_FLASH_ON' {
				print "Switch Flash On";
				$phone_status->{'flash_state'} = 'on';
			}
			case 'OK_FLASH_OFF' {
				print "Switch Flash Off";
				$phone_status->{'flash_state'} = 'off';
			}
			case 'OK_FLASH_AUTO' {
				print "Switch Flash Auta";
				$phone_status->{'flash_state'} = 'auto';
			}
			case 'BAD_SUID' { print "Bad SUID" }
			else            { print $decodedResponse }

		}
	}
}

sub SendSnapshot {

	my $data         = $_[0];
	my $numBytesRead = $_[1];

	my $url =
	    "http://$serverAddress:$portNumber/ttux/01/snapshotResponse/" . $SUID
	  . "/snap"
	  . $frameSeqNo . ".jpg";

	my $r = new HTTP::Request 'PUT', $url;
	$r->header( 'content-length' => $numBytesRead );
	$r->header( 'content-type'   => 'image/jpeg' );
	$r->content($data);
	$response = $ua->request($r);
}

sub SendPing {

	my $url =
	  "http://$serverAddress:$portNumber/ttux/01/ping/" . $SUID . "\n";
	#print $url;
	#print to_json($phone_status) . "\n";
	my $r = new HTTP::Request 'POST', $url;
	$r->header( 'content-type' => 'application/json' );
	$r->content( to_json($phone_status) );
	my $ua       = LWP::UserAgent->new;
	my $response = $ua->request($r);
	return $response;
}

#close($sock);

