#################################################################################
# @file views.py
# @brief  Telmedx url handlers. This is the main code for the site
# @author Tereus Scott
# Creation Date  Sept 28, 2011
# Copyright 2013 telmedx
#  
# Major Revision History
#    Date         Author          Description
#    July 2012    Tereus Scott    Initial implementation
#################################################################################
"""Module views.py
The main view handlers for all incoming http requests
"""
#from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import logout
from django.template import RequestContext
from ttux.models import mobileCam # get our database model
import gevent
#import gevent.queue
from django.views.decorators.csrf import csrf_exempt
from ttux.session import Session
import socket
import errno
import base64
import json
import string
import random
import json

import logging
logger = logging.getLogger("views")
logging.basicConfig(level=logging.INFO)

import ttux_constants as C

##################################################################################
# Constants
##################################################################################
## RETURN CODES
#RC_BAD_SUID = "BAD_SUID"
#
## HTTP STATUS CODES
#HSTAT_OK        = 200
#HSTAT_AUTH_FAIL = 418

##################################################################################
# Globals
##################################################################################
streamRunning=False

##################################################################################
# Helpers
##################################################################################
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """generate a random six digit string"""
    return ''.join(random.choice(chars) for x in range(size))


##################################################################################
# Phone Handlers
##################################################################################
# process a single video frame from the phone
# csrf_exempt decorator is required to allow a post without a csrf token
@csrf_exempt
def rxImage(request, device_name):
    """handler to receive a single video frame from the phone"""
    #print "got img for device " + device_name
    session = Session.get( device_name )
    if session == None:
        print("ERROR: rxImage, no session for SUID: " + device_name)
        return HttpResponse(status=C.HSTAT_AUTH_FAIL, content=C.RC_BAD_SUID)
    
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
    #endif
    ##return HttpResponse(status="200 OK")
    return HttpResponse(status=C.HSTAT_OK, content=command_resp)
#END
    
    
# receive snapshot response from the phone
@csrf_exempt
def snapshotResponse(request, device_name):
    """handler to receive the snapshot response from the phone. This will be posted to the snapshot queue in the session.
    There will be one and only one listener for this snapshot"""
    print "got snapshot response from device: " + device_name
    image = request.read();
    
    session = Session.get( device_name )
    try:
        session.snapshotQ.put_nowait(image)
    except:
        #logger.error("failed to queue up snapshot response")
        print "failed to queue up snapshot response from " + device_name
        session.snapshotQ.get_nowait()  # empty the queue if full
        session.snapshotQ.put_nowait(image)
    #END
    
    return HttpResponse("snapshotResponse")
#END


# handle ping request from the phone
#TODO complete the implementation of PING handling:
# add ability to send back commands like we do in rxImage, both of these methods have the ability to send a command back to the phone
@csrf_exempt
def pingRequest(request, device_name):
    """handler to receive the ping request from the phone"""
    logger.info("PING: got key: " + device_name )
    
    #TODO add payload parsing for device state information: this information needs to be passed back to the UI
    
    # TODO add command handling here: check the command queue and send next command to device if there is one
    response = HttpResponse("OK_PONG")
    response['Content-Type'] = "text/html"
    response['Cache-Control'] = 'no-cache'
    #response['Connection'] = 'keep-alive'
    return(response)
#END

# register session key request from the phone
# TODO need to add some authentication for the phone itself here?
@csrf_exempt
def registerKey(request, key):
    """get four digit session key from the phone and return the SUID from the session object
    If we fail to find the key, then we must return an empty SUID
    """
    logger.info("got key: " + key )
    logger.info("got device_profile")
    resp_data = request.read()
    logger.info( resp_data )
    try:
        resp_data = json.loads( resp_data )
    except:
        response = HttpResponse(status=C.HSTAT_BAD_REQUEST)
        return(response)
    
    # TODO add device profile processing and storage in database
    
    # look up key in session list
    resp_SUID=""
    resp_result=""
    http_response = C.HSTAT_OK
    try:
        resp_SUID = Session.get_SUID(key)
        # TODO need to replace the string 'none' with a constant here and in get_SUID()
        if (resp_SUID == "none"):
            resp_result = C.RC_REGISTER_FAIL
            resp_SUID=""
            http_response = C.HSTAT_OK
            # TODO should we return a different http status here?
        else:
            # SUCCESS, we found the Ticket and got a valid SUID
            resp_result = C.RC_REGISTER_OK
            http_response = C.HSTAT_OK
    except:
        resp_result = C.RC_REGISTER_FAIL
        resp_SUID=""
        http_response = C.HSTAT_OK
    
    # format and send http response
    respData = json.dumps( [ { 'result':resp_result, 'SUID':resp_SUID } ] )
    response = HttpResponse(status=http_response, content=respData)
    response['Content-Type'] = "application/json"
    response['Cache-Control'] = 'no-cache'    
    
    return(response)


##################################################################################
# UI Handlers
##################################################################################
def makeNewSession(request):
    logger.info("Making new session for user: " + request.user.username)
    
    try:
        resp_OTUK = Session.makeSession(request)
        resp_result = C.RC_SESSION_OK
        http_status = C.HSTAT_OK
    except(LookupError):
        # major error: server has run out of keys
        logger.error("Unable to generate a new ticket. Server can not create any new sessions.")
        resp_OTUK="0000"
        resp_result = C.RC_SESSION_FAIL
        http_status = C.HSTAT_NO_KEYS_LEFT
    #OK
    respData = json.dumps( [ { 'result':resp_result, 'OTUK':resp_OTUK } ] )
    response = HttpResponse(status=http_status, content=respData )
    response['Content-Type'] = "application/json"
    response['Cache-Control'] = 'no-cache'

    return(response) 


# Main View Finder Device Control View
def viewmaster(request, device_name):
    """handler for the video viewfinder view"""    
    # make sure user is logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    #
    # look up this device
    d = get_object_or_404(mobileCam, name=device_name)
    # HACK: delete the most recent frame, in case one is left over from a previous session
    # this will create a slight artifact for current viewers
    session = Session.get( device_name )
    session.clear_lastFrame()
    
    return render_to_response('ttux/viewmaster.html', {'dev':d}, context_instance=RequestContext(request))
# END


# Main View Finder Device Control View: Ticket Version
def viewmaster_ticket(request):
    """handler for the video viewfinder view"""    
    # make sure user is logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)

    # Get Ticket and SUID
    try:
        OTUK = Session.makeSession(request)
        SUID = Session.peek_SUID(OTUK)
        logger.info("starting session with Ticket#: " + OTUK)
        logger.info("SUID:" + SUID)
    except:
        logger.error('unable to make a new session')
        response = HttpResponse(status=C.HSTAT_NO_KEYS_LEFT, content="Internal error: no keys left")
        return response
    #END
    
    return render_to_response('ttux/viewmaster.html', {'OTUK':OTUK, 'SUID':SUID}, context_instance=RequestContext(request))
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


# POST request from the UI to take a snapshot 
#@condition(etag_func=None)
@csrf_exempt
def snapshotRequest(request, device_name):
    #return HttpResponse("snapshotRequest")
    #logger.info("Snapshot request from %s", env["REMOTE_ADDR"] )
    print "Snapshot request for device: " + device_name + " from " + request.META["REMOTE_ADDR"] 
    
    # send command to the phone
    session = Session.get( device_name )
    
    ##path = request.META["PATH_INFO"]
    
    # clear any previous frames that might be stuck in the queue 
    if not session.snapshotQ.empty():
        print "oops, found an errant snapshot, flushing the queue"
        #snapshot = session.snapshotQ.get(block=True, timeout=1)
        session.snapshotQ.get(block=True, timeout=1)
    
    path="/snapshot" 
    try:
        session.commandQ.put_nowait(path)
    except:
        session.commandQ.get_nowait()   # remove item if the queue is blocked to keep stale requests from sitting in the queue
    
    # wait for response from the phone
    snapshot = ""
    try:
        snapshot = session.snapshotQ.get(block=True, timeout=10)
    except:
        ##logger.info("failed to get snapshot from phone")
        print("failed to get snapshot from phone " + device_name)
    
    response = { "image" : base64.encodestring(snapshot) }
#    start_response("200 OK", [("Content-Type", "application/json")])
#    return [json.dumps(response)]
    response = HttpResponse(json.dumps(response)) 
    response['Content-Type'] = "application/json"
    print "returning snapshot response now"
    
    return response
#END
    
    
# Device selection View
def deviceView(request):
    # make sure user is logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    
    #deviceList = mobileCam.objects.all().order_by('name')[:4]
    g = request.user.groups.all
    deviceList = mobileCam.objects.filter(groups = g)
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


# Log out
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/?next=%s' % request.path)
#END

