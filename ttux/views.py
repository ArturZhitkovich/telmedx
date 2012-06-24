# TTUX views

from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import logout
from django.template import RequestContext

from ttux.models import mobileCam # get our database model

#from time import sleep
import gevent
import gevent.queue

from django.views.decorators.http import condition
from django.views.decorators.csrf import csrf_exempt

from ttux.session import Session
import socket
import errno
import base64
import json

streamRunning=False
commandQ = gevent.queue.Queue(1)
snapshotQ = gevent.queue.Queue(1)

##################################################################################
# Phone Handlers
##################################################################################
# process a single video frame from the phone
# csrf_exempt decorator is required to allow a post without a csrf token
@csrf_exempt
def rxImage(request, device_name):
    #session = Session.get(0)
    session = Session.get( device_name )
    
    image = request.read();
    # distribute this frame to each watcher
    session.enqueue_frame(image)
    
    # see if there are any commands to send
    try:
        command_resp = commandQ.get_nowait();
    except:
        command_resp = ""
    
    if (command_resp != ""):
        #logger.info("sending command to the phone: %s", command_resp)   
        print("sending command to the phone: %s", command_resp)
         
    ##return HttpResponse(status="200 OK")
    return HttpResponse(command_resp)
    
    
# receive snapshot response from the phone
@csrf_exempt
def snapshotResponse(request):
    print("got snapshot response from the phone")
    image = request.read();
    try:
        snapshotQ.put_nowait(image)
    except:
        #logger.error("failed to queue up snapshot response")
        print("failed to queue up snapshot response")
        snapshotQ.get_nowait()  # empty the queue if full
        snapshotQ.put_nowait(image)
    
    
    return HttpResponse("snapshotResponse")


# handle ping request from the phone
@csrf_exempt
def pingRequest(request):
    response = HttpResponse("pong")
    response['Content-Type'] = "text/html"
    response['Cache-Control'] = 'no-cache'
    #response['Connection'] = 'keep-alive'
    return(response)


##################################################################################
# UI Handlers
##################################################################################

# Main View Finder Device Control View
def index(request, device_name):
    # make sure user is logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    #
    # look up this device
    d = get_object_or_404(mobileCam, name=device_name)

    return render_to_response('ttux/index.html', {'dev':d}, context_instance=RequestContext(request))


# Video stream generator
def stream_response_generator(remote_address, device_name):
    print ("starting stream for remote_addr: " + remote_address + ", device: " + device_name)
    # get the session for this device if it is there
    ## session = Session.get(0)
    session = Session.get( device_name )
    
    #TODO need to use userid here and some kind of session key. remote address is not good enough.
    # this will fail if we use two viewers from the same address. This can happen in a lan/proxy 
    frames = session.add_viewer(remote_address)
    
    try:
        for frame in frames:
            yield( '--myboundary\r\nContent-Type: image/jpeg\r\nContent-Length: %s\r\n\r\n' % ( len(frame) ) )
            yield( frame )
            yield( '\r\n')
            gevent.sleep(0) # allow other events to be processed
            
    except socket.error, e:
        if e[0] not in [errno.ECONNABORTED, errno.ECONNRESET]:
            raise
        
    finally:
        session.remove_viewer( remote_address )
        print("Viewer left: ", remote_address )
        #logger.info("Viewer left: %s", env["REMOTE_ADDR"] )



# open video stream request from browser
@csrf_exempt
def getStreamRequest(request, device_name):
    print("got stream start request for device " + device_name)
    res = HttpResponse(    stream_response_generator( request.META['REMOTE_ADDR'], device_name) )
    res['Content-Type'] = "multipart/x-mixed-replace; boundary=--myboundary"
    res['Media-type'] = 'image/jpeg'
    res['Cache-Control'] = 'no-cache'
    return res


# request from the UI to start a streaming session
def inviteRequest(request):
    return HttpResponse("inviteRequest")

# request from UI to stop the streaming session
def stopRequest(request):
    return HttpResponse("stopRequest")

# POST request from the UI to take a snapshot 
#@condition(etag_func=None)
@csrf_exempt
def snapshotRequest(request):
    #return HttpResponse("snapshotRequest")
    #logger.info("Snapshot request from %s", env["REMOTE_ADDR"] )
    print("Snapshot request from %s", request.META["REMOTE_ADDR"] )
    
    # send command to the phone
    ##path = request.META["PATH_INFO"]
    path="/snapshot" 
    try:
        commandQ.put_nowait(path)
    except:
        commandQ.get_nowait()   # remove item if the queue is blocked to keep stale requests from sitting in the queue
    
    # wait for response from the phone
    snapshot = ""
    try:
        snapshot = snapshotQ.get(block=True, timeout=10)
    except:
        ##logger.info("failed to get snapshot from phone")
        print("failed to get snapshot from phone")
    
    response = { "image" : base64.encodestring(snapshot) }
#    start_response("200 OK", [("Content-Type", "application/json")])
#    return [json.dumps(response)]
    response = HttpResponse(json.dumps(response)) 
    response['Content-Type'] = "application/json"
    return response
    
    
# Device selection View
def deviceView(request):
    # make sure user is logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
        
    deviceList = mobileCam.objects.all().order_by('name')[:4]
    t = loader.get_template('ttux/devices.html')
    c = Context( { 'deviceList':deviceList} )
    return HttpResponse(t.render(c))

    
# Log out
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/?next=%s' % request.path)





