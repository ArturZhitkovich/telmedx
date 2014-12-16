# TTUX views

from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.template import RequestContext

from django.utils.http import urlencode

from ttux.models import mobileCam # get our database model
from ttux.settings import API_KEYS

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
import datetime
import time

import string
import random

##################################################################################
# Globals
##################################################################################
streamRunning=False
#commandQ = gevent.queue.Queue(1)
#snapshotQ = gevent.queue.Queue(1)


##################################################################################
# Helpers
##################################################################################

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


##################################################################################
# Phone Handlers
##################################################################################
# process a single video frame from the phone
# csrf_exempt decorator is required to allow a post without a csrf token
@csrf_exempt
def rxImage(request, device_name):
    #session = Session.get(0)
    #print "got img for device " + device_name
    session = Session.get( device_name )
    
    image = request.read();
    # distribute this frame to each watcher
    session.enqueue_frame(image)
    
    # see if there are any commands to send
    try:
        #command_resp = commandQ.get_nowait();
        command_resp = session.commandQ.get_nowait();
    except:
        command_resp = ""
    
    if (command_resp != ""):
        #logger.info("sending command to the phone: %s", command_resp)   
        print "sending command " + command_resp + " to the phone: " + device_name
    #ENDIF
    ##return HttpResponse(status="200 OK")
    return HttpResponse(command_resp)
#END
    
    
# receive snapshot response from the phone
@csrf_exempt
def snapshotResponse(request, device_name):
    print "got snapshot response from device: " + device_name
    image = request.read();
    
    session = Session.get( device_name )
    try:
        session.snapshotQ.put_nowait(image)
        session.add_snapshot_count()
    except:
        #logger.error("failed to queue up snapshot response")
        print "failed to queue up snapshot response from " + device_name
        session.snapshotQ.get_nowait()  # empty the queue if full
        session.snapshotQ.put_nowait(image)
        session.add_snapshot_count()
    #END
    
    return HttpResponse("snapshotResponse")
#END

@csrf_exempt
def flashlightResponse(request, device_name, status):
    print "got flashlight from device" + device_name

    session = Session.get( device_name )

    try:
        session.flashlightQ.put_nowait( status )
    except:
        #logger.error("failed to queue up snapshot response")
        print "failed to queue up snapshot response from " + device_name
        session.flashlightQ.get_nowait()  # empty the queue if full
        session.flashlightQ.put_nowait( status )
    #END
    
    return HttpResponse("flashlightResponse")

@csrf_exempt
def flipcameraResponse(request, device_name, status):
    print "got camera from device" + device_name

    session = Session.get( device_name )

    try:
        session.flipcameraQ.put_nowait( status )
    except:
        #logger.error("failed to queue up snapshot response")
        print "failed to queue up snapshot response from " + device_name
        session.flipcameraQ.get_nowait()  # empty the queue if full
        session.flipcameraQ.put_nowait( status )
    #END
    
    return HttpResponse("flipcameraResponse")


# handle ping request from the phone
@csrf_exempt
def pingRequest(request):
    response = HttpResponse("pong")
    response['Content-Type'] = "text/html"
    response['Cache-Control'] = 'no-cache'
    #response['Connection'] = 'keep-alive'
    return(response)
#END
@csrf_exempt
def ping2Request(request, app_version, device_name):
    if( app_version is not None and device_name is not None and not device_name == ''):
        print device_name
        print app_version
        if app_version == '1.0.0': #Has flip camera & flashlight
            
            session = Session.get( device_name )
            if session is not None:

                # print json.dumps({'status':'ok' ,'command':'update_controls', 'parameters':['flip', 'flash']})
                try:
                    session.deviceSpecQ.put_nowait( json.dumps({'status':'ok' ,'command':'update_controls', 'parameters':['flip', 'flash']}) )
                except:
                    session.deviceSpecQ.get_nowait()   # remove item if the queue is blocked to keep stale requests from sitting in the queue
            

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
# END


# Main View Finder Device Control View
# for testing XHR
def index2(request, device_name):
    # make sure user is logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    #
    # look up this device
    d = get_object_or_404(mobileCam, name=device_name)

    return render_to_response('ttux/index2.html', {'dev':d}, context_instance=RequestContext(request))
# END


# Main View Finder Device Control View
# for testing jquery XHR
def index3(request, device_name):
    # make sure user is logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    #
    print device_name
    device_name = device_name.strip()
    # look up this device
    d = get_object_or_404(mobileCam, name=device_name)
    # HACK: delete the most recent frame, in case one is left over from a previous session
    # this will create a slight artifact for current viewers
    session = Session.get( device_name )
    session.clear_lastFrame()

    return render_to_response('ttux/index3.html', {'dev':d}, context_instance=RequestContext(request))
# END



# Video stream generator
def stream_response_generator(remote_address, device_name):
    print ("starting stream for remote_addr: " + remote_address + ", device: " + device_name)
    # get the session for this device if it is there
    ## session = Session.get(0)
    session = Session.get( device_name )
    
    #TODO need to use userid here and some kind of session key. remote address is not good enough.
    # this will fail if we use two viewers from the same address. This can happen in a lan/proxy
    viewer_key = remote_address + ":" +  id_generator(6)
    frames = session.add_viewer(viewer_key)
    
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
        session.remove_viewer( viewer_key )
        print("Viewer left: ", viewer_key )
        #logger.info("Viewer left: %s", env["REMOTE_ADDR"] )

# END def


# XHR video stream generator SOF/EOF: sends back binary data
def stream_response_generator_XHR_SOFEOF(remote_address, device_name):
    print ("starting stream for remote_addr: " + remote_address + ", device: " + device_name)
    # get the session for this device if it is there
    ## session = Session.get(0)
    session = Session.get( device_name )
    
    #TODO need to use userid here and some kind of session key. remote address is not good enough.
    # this will fail if we use two viewers from the same address. This can happen in a lan/proxy
    viewer_key = remote_address + ":" +  id_generator(6)
    frames = session.add_viewer(viewer_key)
    
    try:
        for frame in frames:
            encodedResp = base64.encodestring(frame)
            ## yield( '--myboundary\r\nContent-Type: image/jpeg\r\nContent-Length: %s\r\n\r\n' % ( len(frame) ) )
            yield( '--SOF--' )
            ## yield( frame )
            yield(encodedResp)
            yield( '--EOF--')
            ## yield( '\r\n')
            gevent.sleep(0) # allow other events to be processed
            
    except socket.error, e:
        if e[0] not in [errno.ECONNABORTED, errno.ECONNRESET]:
            raise
        
    finally:
        session.remove_viewer( viewer_key )
        print("Viewer left: ", viewer_key )
        #logger.info("Viewer left: %s", env["REMOTE_ADDR"] )

# END def



#########################################################################################
#########################################################################################
# Testing Chunked Response
# XHR video stream generator SOF/EOF: sends back binary data



def stream_response_generator_XHR_SOFEOF_chunked(remote_address, device_name):
    print ("starting stream for remote_addr: " + remote_address + ", device: " + device_name)
    # get the session for this device if it is there
    ## session = Session.get(0)
    session = Session.get( device_name )
    
    #TODO need to use userid here and some kind of session key. remote address is not good enough.
    # this will fail if we use two viewers from the same address. This can happen in a lan/proxy
    viewer_key = remote_address + ":" +  id_generator(6)
    frames = session.add_viewer(viewer_key)
    
    try:
        # send chunked frame resonse
        for frame in frames:
            encodedResp = base64.encodestring(frame)
            yield( '%s\r\n' % ( len(frame) ) )
            yield( '--SOF--' )
            ## yield( frame )
            yield(encodedResp)
            yield( '--EOF--')
            ## yield( '\r\n')
            gevent.sleep(0) # allow other events to be processed
            
    except socket.error, e:
        if e[0] not in [errno.ECONNABORTED, errno.ECONNRESET]:
            raise
        
    finally:
        session.remove_viewer( viewer_key )
        print("Viewer left: ", viewer_key )
        #logger.info("Viewer left: %s", env["REMOTE_ADDR"] )

# END def


@csrf_exempt
def getStreamRequest_XHR_Chunked(request, device_name):
    print("got stream start request for device " + device_name)
    res = HttpResponse(    stream_response_generator_XHR_SOFEOF_chunked( request.META['REMOTE_ADDR'], device_name) )
    #res['Content-Type'] = "multipart/x-mixed-replace; boundary=--myboundary"
    res['Content-Type'] = "image/jpeg"
    res['Content-Encoding'] = "chunked"
    #res['Transfer-Encoding'] = "chunked"
    #res['Media-type'] = 'image/jpeg'
    res['Cache-Control'] = 'no-cache'
    #res['Connection'] = 'keep-alive'
    return res
# END

#########################################################################################
#########################################################################################





# XHR stream generator for testing, sends back strings.
def stream_response_generator_XHR(remote_address, device_name):
    print ("starting HXR stream for remote_addr: " + remote_address + ", device: " + device_name)
    # get the session for this device if it is there
    #session = Session.get( device_name )
    
    for x in range(0,9):
        print ("say hello %d", x)
        frame = "hello %d 12345678990123456789901234567899012345678990123456789901234567899012345678990123456789901234567899012345678990" % (x)
        #yield( '--myboundary\r\nContent-Type: text/plain\r\nContent-Length: %s\r\n\r\n' % ( len(frame) ) )
        yield( '--SOF--' )
        gevent.sleep(1)
        yield( frame )
        yield( '--EOF--')
        #yield('----EOF----'); # end of frame marker
        #yield('extra text test, this should be in the next buffer\r\n')
        gevent.sleep(2) # allow other events to be processed
    #endfor      
    print("Viewer left")


# END def




# open video stream request from browser flash app
@csrf_exempt
def getStreamRequest(request, device_name):
    print("got stream start request for device " + device_name)
    res = HttpResponse(    stream_response_generator( request.META['REMOTE_ADDR'], device_name) )
    res['Content-Type'] = "multipart/x-mixed-replace; boundary=--myboundary"
    res['Media-type'] = 'image/jpeg'
    res['Cache-Control'] = 'no-cache'
    return res
# END

#########################################################################
# simple text stream generator to test xmlhttprequest, 
# this uses a multi-part response type
@csrf_exempt
def getStreamRequest_XHR(request, device_name):
    print("got stream start request for device " + device_name)
    ## res = HttpResponse(    stream_response_generator_XHR( request.META['REMOTE_ADDR'], device_name) )
    res = HttpResponse(    stream_response_generator_XHR_SOFEOF( request.META['REMOTE_ADDR'], device_name) )
    res['Content-Type'] = "multipart/x-mixed-replace; boundary=--myboundary"
    res['Media-type'] = 'image/jpeg'
    res['Cache-Control'] = 'no-cache'
    return res
# END



#######################################################################
# single url to return the most recent frame
def getLastFrameFromStream(request, device_name, fnum):



    fnum_padded = str(fnum).zfill(8)
    #fnum_padded = fnum
    #print("got request for the most recent frame for device: " + device_name + "frame num: " + fnum + " " + fnum_padded)
    session = Session.get( device_name )

    # check if we are asking for the same frame again    
    lastFnumber = session.get_frameNumber()
    lastFnumber_str = str(lastFnumber).zfill(8)
    #print ("current frame: " + lastFnumber_str )
    
    # do not send a response until the frame changes, cheat and just sleep for now
    if ( fnum == lastFnumber_str ):
        #print("duplicate frame, pause")    
        timeout = 1000 # when to bail out
        while  ( ( fnum == lastFnumber_str ) and (timeout > 0) ):
            timeout -= 1
            gevent.sleep(0.01)
            lastFnumber = session.get_frameNumber()
            lastFnumber_str = str(lastFnumber).zfill(8)
        #while
    #if        
        
    frame = session.get_lastFrame()
    lastFnumber = session.get_frameNumber()
    lastFnumber_str = str(lastFnumber).zfill(8)

    try:
        lastFnumber_str = '!!'+session.deviceSpecQ.get_nowait()+'!!'+lastFnumber_str
    except Exception, e:
        pass
        
    #print ("current frame: " + lastFnumber_str )
        
    encodedResp = lastFnumber_str + base64.encodestring(frame)
    response = HttpResponse(encodedResp)
    response['Content-Type'] = "text/html"
    #response['Content-Type'] = "image/jpeg"
    response['Cache-Control'] = 'no-cache'
    return(response)
#END



# request from the UI to start a streaming session
def inviteRequest(request):
    return HttpResponse("inviteRequest")
#END


# request from UI to stop the streaming session
def stopRequest(request):
    return HttpResponse("stopRequest")
#END

@csrf_exempt
def flipCamera(request, device_name):
    print "Flip camera for device: " + device_name + " from " + request.META["REMOTE_ADDR"]

    session = Session.get( device_name )

    if not session.flipcameraQ.empty():
        print "oops, found an errant flashlight, flushing the queue"
        snapshot = session.flipcameraQ.get(block=True, timeout=1)
    
    path="/flipcamera" 

    try:
        session.commandQ.put_nowait(path)
    except:
        session.commandQ.get_nowait()   # remove item if the queue is blocked to keep stale requests from sitting in the queue
    
    status = ""
    try:
        status = session.flipcameraQ.get(block=True, timeout=20)
    except:
        ##logger.info("failed to get snapshot from phone")
        print("failed to get flip from phone " + device_name)
    
    response = { "status" : status }
#    start_response("200 OK", [("Content-Type", "application/json")])
#    return [json.dumps(response)]
    response = HttpResponse(json.dumps(response)) 
    response['Content-Type'] = "application/json"
    print "returning flashlight response now"
    
    return response


@csrf_exempt
def toggleFlash(request, device_name):
    print "Toggle Flashlight request for device: " + device_name + " from " + request.META["REMOTE_ADDR"] 

    session = Session.get( device_name )

    if not session.flashlightQ.empty():
        print "oops, found an errant flashlight, flushing the queue"
        snapshot = session.flashlightQ.get(block=True, timeout=1)
    
    path="/toggleflash" 

    try:
        session.commandQ.put_nowait(path)
    except:
        session.commandQ.get_nowait()   # remove item if the queue is blocked to keep stale requests from sitting in the queue
    
    status = ""
    try:
        status = session.flashlightQ.get(block=True, timeout=20)
    except:
        ##logger.info("failed to get snapshot from phone")
        print("failed to get snapshot from phone " + device_name)
    
    response = { "status" : status }
#    start_response("200 OK", [("Content-Type", "application/json")])
#    return [json.dumps(response)]
    response = HttpResponse(json.dumps(response)) 
    response['Content-Type'] = "application/json"
    print "returning flashlight response now"
    
    return response

# POST request from the UI to take a snapshot 
#@condition(etag_func=None)
@csrf_exempt
def snapshotRequest(request, device_name):
    #return HttpResponse("snapshotRequest")
    #logger.info("Snapshot request from %s", env["REMOTE_ADDR"] )
    print "Snapshot request for device: " + device_name + " from " + request.META["REMOTE_ADDR"] 
    # import pdb; pdb.set_trace()

    # send command to the phone
    session = Session.get( device_name )
    
    ##path = request.META["PATH_INFO"]
    
    # clear any previous frames that might be stuck in the queue 
    if not session.snapshotQ.empty():
        print "oops, found an errant snapshot, flushing the queue"
        snapshot = session.snapshotQ.get(block=True, timeout=1)
    
    path="/snapshot" 
    try:
        session.commandQ.put_nowait(path)
    except:
        session.commandQ.get_nowait()   # remove item if the queue is blocked to keep stale requests from sitting in the queue
    


    
    if request.POST.get('ie','false') == 'false':
        # wait for response from the phone
        snapshot = ""
        try:
            snapshot = session.snapshotQ.get(block=True, timeout=20)
        except:
            ##logger.info("failed to get snapshot from phone")
            print("failed to get snapshot from phone " + device_name)

        response = { "image" : base64.encodestring(snapshot) }
    else:
        response = { 'link': True }
#    start_response("200 OK", [("Content-Type", "application/json")])
#    return [json.dumps(response)]
    response = HttpResponse(json.dumps(response)) 
    response['Content-Type'] = "application/json"
    print "returning snapshot response now"
    
    return response
#END

def get_ie_snapshot(request, device_name, salt):

    session = Session.get( device_name )
    snapshot = ""
    try:
        snapshot = session.snapshotQ.get(block=True, timeout=20)
    except:
        ##logger.info("failed to get snapshot from phone")
        print("failed to get snapshot from phone " + device_name)
        return HttpResponse("")

    return HttpResponse(snapshot, mimetype="image/png")

def view_session_info(request):
    device = request.GET.get('device',None)
    body = 'devicenotfound'
    if device is not None:
        session = Session.get( device )
        body = 'begin timestamp:   '+str(session.begin_timestamp)+'<br>'
        body += 'end timestamp:   '+str(session.last_frame_timestamp)+'<br>'
        body += 'frames in session:   '+str(session.frames_in_session)+'<br>'
        body += 'difference:   '+str(time.time() - session.last_frame_timestamp)+'<br>'
        body += 'cleaning...<br>'
        session.clean_session()
        body += 'begin timestamp:   '+str(session.begin_timestamp)+'<br>'
        body += 'end timestamp:   '+str(session.last_frame_timestamp)+'<br>'
        body += 'frames in session:   '+str(session.frames_in_session)+'<br>'
    return HttpResponse(body)
    
# Device selection View
def deviceView(request):
    # make sure user is logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    
    #deviceList = mobileCam.objects.all().order_by('name')[:4]
    g = request.user.groups.all
    deviceList = mobileCam.objects.filter(groups = g).order_by('name')
    # refresh the session list. This will add a new session if there is a new device
    # but will not change any existing sessions.
    # TODO this needs to be done on the admin page when a new device is added to the database. 
    for d in deviceList:
        Session.put(d.name, Session())
    
    #    t = loader.get_template('ttux/devices.html')
    #    c = Context( { 'deviceList':deviceList} )
    #    return HttpResponse(t.render(c))
    #
    return render_to_response('ttux/devices.html', {'deviceList':deviceList}, context_instance=RequestContext(request))
#END

def sso_login_view(request, device_name):
    key = request.GET.get('key','1111')
    if key in API_KEYS:
        username = API_KEYS[key]
        user = get_object_or_404(User, username=username)
        user.backend='django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return HttpResponseRedirect('/device/'+device_name)
    else:
        return HttpResponse('Not Authorized')

@csrf_exempt
def initialize_device(request):
    if request.method == "POST":
        try:
            json_data = json.loads(request.body)
        except Exception:
            return HttpResponse('Invalid Body')
        key = json_data.get('api-key','1111')
        if key in API_KEYS:
            username = API_KEYS[key]
            user = get_object_or_404(User, username=username)
        try:
            g = user.groups.all()[0]
            device_name = json_data.get('email','')
        except Exception:
            return HttpResponse('Invalid Body')
        try:
            cam = mobileCam.objects.get(name=device_name)
            cam.last_name = json_data.get('lastName','')
            cam.first_name = json_data.get('firstName','')
            cam.phone_number = json_data.get('phoneNumber','')
            cam.email = json_data.get('email','')
            cam.save()
        except Exception:
            cam = mobileCam.objects.create(groups = g, 
                last_name=json_data.get('lastName',''), 
                first_name=json_data.get('firstName',''), 
                phone_number=json_data.get('phoneNumber',''),
                email=json_data.get('email',''),
                name=device_name
                )
        session = Session.get( device_name )
        if session is None:
            Session.put(device_name, Session())

        return HttpResponse(json.dumps({'status':'ok','device_name':cam.name}), content_type='application/json')


# Log out
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/?next=%s' % request.path)
#END

