# TTUX views


#from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.template import RequestContext

from polls.models import Poll
#from time import sleep
import gevent
import gevent.queue

from django.views.decorators.http import condition
from django.views.decorators.csrf import csrf_exempt

from polls.session import Session
import socket
import errno

streamRunning=False
commandQ = gevent.queue.Queue(1)
snapshotQ = gevent.queue.Queue(1)

def index(request):
# make sure user is logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    #sleep(30)
    return render_to_response('ttux/index.html', context_instance=RequestContext(request))


# process a single video frame from the phone
# csrf_exempt decorator is required to allow a post without a csrf token
@csrf_exempt
def rxImage(request):
    session = Session.get(0)
    
    print "host:" + request.get_host()
    print "method: " + request.method
    
    # req.raw_post_data and req.read() will give the same data.
    print 'raw_post_data:"%s"' % request.raw_post_data
    image = request.read();
    print "request.read(): " + image
    
    # distribute this frame to each watcher
    session.enqueue_frame(image)
        
#    if request.method == 'GET':
#        do_something()
#    elif request.method == 'POST':
#        do_something_else()
    return HttpResponse(status="200 OK")
    
# process snapshot response from the phone
@csrf_exempt
def snapshotResponse(request):
    return HttpResponse("snapshotResponse")



def stream_response_generator(remote_address):
    print ("starting stream for remote_addr: " + remote_address)
    session = Session.get(0)
    #TODO need to use userid here and some kind of session key. remote address is not good enough.
    # this will fail if we use two viewers from the same address. This can happen in a lan/proxy 
    frames = session.add_viewer(remote_address)
    
    try:
        for frame in frames:
            #yield( '--myboundary\r\nContent-Type: image/jpeg\r\nContent-Length: %s\r\n\r\n' % ( len(frame) ) )
            yield( '--myboundary\r\nContent-Type: text/html\r\nContent-Length: %s\r\n\r\n' % ( len(frame) ) )
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
def getStreamRequest(request):
    res = HttpResponse(    stream_response_generator(request.META['REMOTE_ADDR']) )
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

# request from the UI to take a snapshot
def snapshotRequest(request):
    return HttpResponse("snapshotRequest")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/?next=%s' % request.path)





