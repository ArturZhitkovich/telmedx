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

import socket
import errno

streamRunning=False
commandQ = gevent.queue.Queue(1)
snapshotQ = gevent.queue.Queue(1)

def index(request):
#    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
#    t = loader.get_template('polls/index.html')
#    c = Context({
#        'latest_poll_list': latest_poll_list,
#    })
#    return HttpResponse(t.render(c))

# make sure user is logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    #sleep(30)
    return render_to_response('polls/index.html', context_instance=RequestContext(request))

#def rxImage(request):
#    #print request.wsgi_input
#    #return HttpResponse("hi")
#    #resp = HttpResponse(content, mimetype, status, content_type)
#    resp = HttpResponse(status="200 OK");
#    resp['Content-Type']  = "multipart/x-mixed-replace; boundary=--myboundary"
#    #resp['Media-type']    = "image/jpeg"
#    resp['Media-type']    = "text/html"
#    resp['Cache-Control'] = 'no-cache'
#    
#    test=0
#    while (test < 20):
#        print "Hi" + str(test)
#        resp.write("Hi" + str(test) )
#        gevent.sleep(5)
#        test = test + 1

# Streaming Example
#@condition(etag_func=None)
#def rxImage(request):
#    resp = HttpResponse( stream_response_generator(), mimetype='text/html')
#    return resp
#
#def stream_response_generator():
#    yield "<html><body>\n"
#    for x in range(1,11):
#        yield "<div>%s</div>\n" % x
#        #yield " " * 1024  # Encourage browser to render incrementally
#        gevent.sleep(2)
#    yield "</body></html>\n"

# process a single video frame from the phone
# csrf_exempt decorator is required to allow a post without a csrf token
@csrf_exempt
def rxImage(request):
    
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
    #return HttpResponse("rxImage: </br>" + request.get_host() + "</br>" + request.get_full_path() )
    return HttpResponse(status="200 OK")
    
# process snapshot response from the phone
@csrf_exempt
def snapshotResponse(request):
    return HttpResponse("snapshotResponse")



def stream_response_generator(remote_address):
    print ("starting stream for remote_addr: " + remote_address)
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
#        response=env
#                return response;    
#    yield "<html><body>\n"
#    for x in range(1,11):
#        yield "<div>%s</div>\n" % x
#        #yield " " * 1024  # Encourage browser to render incrementally
#        gevent.sleep(1)
#    yield "</body></html>\n"



# open video stream request from browser
@csrf_exempt
def getStreamRequest(request):
    #return HttpResponse(status="200 OK")
    #return HttpResponse("getStreamRequest")

#    return HttpResponse(    stream_response_generator(request.META['REMOTE_ADDR']), \
#                            status="200 OK",             \
#                            mimetype='text/html')

    res = HttpResponse(    stream_response_generator(request.META['REMOTE_ADDR']), \
                            #status="200 OK",
                            )

    #wc = start_response("200 OK", [("Content-Type", "multipart/x-mixed-replace; boundary=--myboundary"), ('Media-type', 'image/jpeg')])
    res['Content-Type'] = "multipart/x-mixed-replace; boundary=--myboundary"
    res['Media-type'] = 'image/jpeg'
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


#def detail(request, poll_id):
#    return HttpResponse("You're looking at poll %s." % poll_id)
#
#def results(request, poll_id):
#    return HttpResponse("You're looking at the results of poll %s." % poll_id)
#
#def vote(request, poll_id):
#    return HttpResponse("You're voting on poll %s." % poll_id)



