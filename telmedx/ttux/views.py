import base64
import errno
import json
import logging
import socket
import time

# from time import sleep
import gevent
import gevent.queue
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from .helpers import id_generator
from .models import mobileCam  # get our database model
from .serializers import InitializeSerializer
from .session import Session
from .settings import API_KEYS

stream_running = False
# commandQ = gevent.queue.Queue(1)
# snapshotQ = gevent.queue.Queue(1)

logger = logging.getLogger(__name__)


##################################################################################
# Phone Handlers
##################################################################################
# process a single video frame from the phone
@csrf_exempt
def rx_image(request, device_name):
    """
    Receive image data from mobile apps.
    This assumes data is sent through in binary mode.

    Example `curl` command:
    ```bash
    curl -X POST --data-binary \
         localhost:8000/ttux/img/user@example.com/img0001.jpg
    ```

    :param request:
    :param device_name:
    :return:
    :rtype: HttpResponse
    """

    # session = Session.get(0)
    # print "got img for device " + device_name
    session = Session.get(device_name)

    if not session:
        return JsonResponse({'status': 'Not ready'})

    image = request.read()
    # distribute this frame to each watcher
    session.enqueue_frame(image)

    # see if there are any commands to send
    try:
        # command_resp = commandQ.get_nowait();
        command_resp = session.commandQ.get_nowait()
    except Exception as e:
        command_resp = ""

    if command_resp != "":
        # logger.info("sending command to the phone: %s", command_resp)
        print("sending command " + command_resp + " to the phone: " + device_name)

    # ENDIF
    ##return HttpResponse(status="200 OK")
    return HttpResponse(command_resp)


@csrf_exempt
def snapshot_response(request, device_name):
    """
    receive snapshot response from the phone
    :param request:
    :param device_name:
    :return:
    """
    print("got snapshot response from device: " + device_name)
    image = request.read()

    session = Session.get(device_name)
    try:
        session.snapshotQ.put_nowait(image)
        session.add_snapshot_count()
    except:
        # logger.error("failed to queue up snapshot response")
        print("failed to queue up snapshot response from " + device_name)
        session.snapshotQ.get_nowait()  # empty the queue if full
        session.snapshotQ.put_nowait(image)
        session.add_snapshot_count()
    # END

    return HttpResponse("snapshot_response")


# END

@csrf_exempt
def flashlight_response(request, device_name, status):
    """
    Receive flashlight response from the phone/mobile device
    :param request:
    :param device_name:
    :param status:
    :return:
    """
    print("got flashlight from device: {}, {}".format(device_name, status))

    session = Session.get(device_name)

    try:
        session.flashlightQ.put_nowait(status)
    except:
        # logger.error("failed to queue up snapshot response")
        print("failed to queue up flashlight response from " + device_name)
        session.flashlightQ.get_nowait()  # empty the queue if full
        session.flashlightQ.put_nowait(status)

    return HttpResponse("flashlightResponse")


@csrf_exempt
def flipcamera_response(request, device_name, status):
    """
    Receive flip camera response from phone/device
    :param request:
    :param device_name:
    :param status:
    :return:
    """
    print("got camera from device" + device_name)

    session = Session.get(device_name)

    try:
        session.flipcameraQ.put_nowait(status)
    except:
        # logger.error("failed to queue up snapshot response")
        print("failed to queue up snapshot response from " + device_name)
        session.flipcameraQ.get_nowait()  # empty the queue if full
        session.flipcameraQ.put_nowait(status)
    # END

    return HttpResponse("flipcameraResponse")


# handle ping request from the phone
@csrf_exempt
def pingRequest(request):
    response = HttpResponse("pong")
    response['Content-Type'] = "text/html"
    response['Cache-Control'] = 'no-cache'
    # response['Connection'] = 'keep-alive'
    return (response)


# END
@csrf_exempt
def ping2_request(request, app_version, device_name):
    """
    This is resposible of handling "new" app versions which support camera
    features such as changing camera (front/back facing) and torch control.

    :param request:
    :param app_version:
    :param device_name:
    :return:
    """
    if all([app_version, device_name]):
        # Has flip camera & flashlight
        if app_version == '1.0.0':

            session = Session.get(device_name)
            if session is not None:
                try:
                    session.deviceSpecQ.put_nowait(
                        json.dumps({
                            'status': 'ok',
                            'command': 'update_controls',
                            'parameters': ['flip', 'flash']
                        })
                    )
                except:
                    # remove item if the queue is blocked to keep stale
                    # requests from sitting in the queue
                    session.deviceSpecQ.get_nowait()

    response = HttpResponse("pong")
    response['Content-Type'] = "text/html"
    response['Cache-Control'] = 'no-cache'
    # response['Connection'] = 'keep-alive'
    return (response)


##################################################################################
# UI Handlers
##################################################################################

# deprecated
def index(request, device_name):
    """
    Main View Finder Device Control View
    :param request:
    :param device_name:
    :return:
    """
    # make sure user is logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    #
    # look up this device
    d = get_object_or_404(mobileCam, name=device_name)

    return render_to_response('ttux/index.html', {'dev': d})


# deprecated
def index2(request, device_name):
    """
    Main View Finder Device Control View for texting XHR
    :deprecated:
    :param request:
    :param device_name:
    :return:
    """
    # make sure user is logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    #
    # look up this device
    d = get_object_or_404(mobileCam, name=device_name)

    return render_to_response('ttux/index2.html', {'dev': d})


def index3(request, device_name):
    """
    Main View Finder Device Control View for testing jquery XHR
    :param request:
    :param device_name:
    :return:
    """
    # make sure user is logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    #
    # look up this device
    d = get_object_or_404(mobileCam, name=device_name)
    # HACK: delete the most recent frame, in case one is left over from a previous session
    # this will create a slight artifact for current viewers
    try:
        session = Session.get(device_name)
        session.clear_lastFrame()
    except AttributeError:
        # Camera is not active yet, so just ignore?
        pass

    return render_to_response('ttux/index3.html', {'dev': d})


# Video stream generator
def stream_response_generator(remote_address, device_name):
    print("starting stream for remote_addr: " + remote_address + ", device: " + device_name)
    # get the session for this device if it is there
    ## session = Session.get(0)
    session = Session.get(device_name)

    # TODO need to use userid here and some kind of session key. remote address is not good enough.
    # this will fail if we use two viewers from the same address. This can happen in a lan/proxy
    viewer_key = remote_address + ":" + id_generator(6)
    frames = session.add_viewer(viewer_key)

    try:
        for frame in frames:
            yield ('--myboundary\r\nContent-Type: image/jpeg\r\nContent-Length: %s\r\n\r\n' % (len(frame)))
            yield (frame)
            yield ('\r\n')
            gevent.sleep(0)  # allow other events to be processed

    except socket.error as e:
        if e[0] not in [errno.ECONNABORTED, errno.ECONNRESET]:
            raise

    finally:
        session.remove_viewer(viewer_key)
        print("Viewer left: ", viewer_key)
        # logger.info("Viewer left: %s", env["REMOTE_ADDR"] )


# END def


@csrf_exempt
def get_stream_request(request, device_name):
    """
    open video stream request from browser flash app
    :param request:
    :param device_name:
    :return:
    """
    print("got stream start request for device " + device_name)
    res = HttpResponse(stream_response_generator(request.META['REMOTE_ADDR'], device_name))
    res['Content-Type'] = "multipart/x-mixed-replace; boundary=--myboundary"
    res['Media-type'] = 'image/jpeg'
    res['Cache-Control'] = 'no-cache'
    return res


def get_last_frame_from_stream(request, device_name, fnum):
    """
    single url to return the most recent frame
    :param request:
    :param device_name:
    :param fnum:
    :return:
    """
    fnum_padded = str(fnum).zfill(8)
    # fnum_padded = fnum
    session = Session.get(device_name)

    if not session:
        return HttpResponse('Not ready')

    try:
        # check if we are asking for the same frame again
        lastFnumber = session.get_frameNumber()
        lastFnumber_str = str(lastFnumber).zfill(8)
        # print ("current frame: " + lastFnumber_str )
    except:
        lastFnumber = ""
        lastFnumber_str = str(lastFnumber).zfill(8)

    # do not send a response until the frame changes,
    # cheat and just sleep for now
    if fnum == lastFnumber_str:
        # when to bail out
        timeout = 1000
        while fnum == lastFnumber_str and timeout > 0:
            timeout -= 1
            gevent.sleep(0.01)
            lastFnumber = session.get_frameNumber()
            lastFnumber_str = str(lastFnumber).zfill(8)

    frame = session.get_lastFrame()
    if frame:
        lastFnumber = session.get_frameNumber()
        lastFnumber_str = str(lastFnumber).zfill(8)

        try:
            lastFnumber_str = '!!{}!!{}'.format(
                session.deviceSpecQ.get_nowait(),
                lastFnumber_str
            )
        except Exception as e:
            pass

        frame_encoded = base64.encodebytes(frame)
        encodedResp = lastFnumber_str + frame_encoded.decode('ascii')
        # encodedResp = base64.encodebytes(frame)
        response = HttpResponse(encodedResp)
        response['Content-Type'] = "text/html"
        # response['Content-Type'] = "image/jpeg"
        response['Cache-Control'] = 'no-cache'
    else:
        response = HttpResponse('0')
        response['Content-Type'] = "text/html"
        response['Cache-Control'] = 'no-cache'

    return response


def invite_request(request):
    """
    request from the UI to start a streaming session
    NOT IMPLEMENTED
    :param request:
    :return:
    """
    return HttpResponse("inviteRequest")


def stop_request(request):
    """
    request from UI to stop the streaming session
    :param request:
    :return:
    """
    return HttpResponse("stopRequest")


@csrf_exempt
def flip_camera(request, device_name):
    """
    Handle flip camera request. This comes from the web interface.
    :param request:
    :param device_name:
    :return:
    """
    print("Flip camera for device: " + device_name + " from " + request.META["REMOTE_ADDR"])

    session = Session.get(device_name)

    if not session.flipcameraQ.empty():
        print("oops, unable to flip camera, flushing the queue")
        snapshot = session.flipcameraQ.get(block=True, timeout=1)

    path = "/flipcamera"

    try:
        session.commandQ.put_nowait(path)
    except:
        # remove item if the queue is blocked to keep stale requests from
        # sitting in the queue
        session.commandQ.get_nowait()

    status = ""
    session = Session.get(device_name)

    try:
        status = session.flipcameraQ.get(block=True, timeout=20)
    except:
        print("failed to get flip from phone " + device_name)

    response = JsonResponse({"status": status})
    print("returning flashlight response now")

    return response


@csrf_exempt
def toggle_flash(request, device_name):
    """
    Handle toggle flash request. This comes from the web interface.
    :param request:
    :param device_name:
    :return:
    """
    print('Toggle flashlight request for device: {} from {}'.format(
        device_name,
        request.META['REMOTE_ADDR']
    ))

    session = Session.get(device_name)

    if not session.flashlightQ.empty():
        print("oops, found an errant flashlight, flushing the queue")
        session.flashlightQ.get(block=True, timeout=1)

    path = "/toggleflash"

    try:
        session.commandQ.put_nowait(path)
    except Exception as e:
        # remove item if the queue is blocked to keep stale requests from
        # sitting in the queue
        session.commandQ.get_nowait()

    status = ""
    try:
        status = session.flashlightQ.get(block=True, timeout=20)
    except:
        print("failed to get snapshot from phone " + device_name)

    response = JsonResponse({"status": status})
    print("returning flashlight response now")

    return response


@csrf_exempt
def snapshot_request(request, device_name):
    """
    POST request from the UI to take a snapshot
    :param request:
    :param device_name:
    :return:
    """
    # return HttpResponse("snapshotRequest")
    # logger.info("Snapshot request from %s", env["REMOTE_ADDR"] )
    print('Snapshot request for device: {} from {}'.format(
        device_name,
        request.META["REMOTE_ADDR"]))

    # send command to the phone
    session = Session.get(device_name)

    # clear any previous frames that might be stuck in the queue
    if not session.snapshotQ.empty():
        print("oops, found an errant snapshot, flushing the queue")
        snapshot = session.snapshotQ.get(block=True, timeout=1)

    path = "/snapshot"
    try:
        session.commandQ.put_nowait(path)
    except:
        # remove item if the queue is blocked to keep stale requests from
        # sitting in the queue
        session.commandQ.get_nowait()

    if request.POST.get('ie', 'false') == 'false':
        # wait for response from the phone
        snapshot = ""
        try:
            snapshot = session.snapshotQ.get(block=True, timeout=20)
        except:
            # logger.info("failed to get snapshot from phone")
            print("failed to get snapshot from phone " + device_name)

        response = {"image": base64.encodebytes(snapshot).decode('utf-8')}
    else:
        response = {'link': True}
    # start_response("200 OK", [("Content-Type", "application/json")])
    #    return [json.dumps(response)]
    response = HttpResponse(json.dumps(response))
    response['Content-Type'] = "application/json"
    print("returning snapshot response now")

    return response


def get_ie_snapshot(request, device_name, salt):
    session = Session.get(device_name)
    snapshot = ""
    try:
        snapshot = session.snapshotQ.get(block=True, timeout=20)
    except:
        print("failed to get snapshot from phone " + device_name)
        return HttpResponse("")

    return HttpResponse(snapshot, mimetype="image/png")


def view_session_info(request):
    device = request.GET.get('device', None)
    body = 'devicenotfound'

    if device is not None:
        session = Session.get(device)
        body = 'begin timestamp:   ' + str(session.begin_timestamp) + '<br>'
        body += 'end timestamp:   ' + str(session.last_frame_timestamp) + '<br>'
        body += 'frames in session:   ' + str(session.frames_in_session) + '<br>'
        body += 'difference:   ' + str(time.time() - session.last_frame_timestamp) + '<br>'
        body += 'cleaning...<br>'
        session.clean_session()
        body += 'begin timestamp:   ' + str(session.begin_timestamp) + '<br>'
        body += 'end timestamp:   ' + str(session.last_frame_timestamp) + '<br>'
        body += 'frames in session:   ' + str(session.frames_in_session) + '<br>'
    return HttpResponse(body)


def device_view(request):
    """
    Device selection View
    :param request:
    :return:
    """
    # make sure user is logged in
    # if not request.user.is_authenticated():
    #     return HttpResponseRedirect('/login/?next=%s' % request.path)
    user = User.objects.first()

    # deviceList = mobileCam.objects.all().order_by('name')[:4]
    # g = request.user.groups.all()
    g = user.groups.all()
    deviceList = mobileCam.objects.filter(groups=g).order_by('name')
    # refresh the session list. This will add a new session if there is a new device
    # but will not change any existing sessions.
    # TODO: needs to be done on the admin page when a new device is added to the database
    for d in deviceList:
        Session.put(d.name, Session())

    # t = loader.get_template('ttux/devices.html')
    #    c = Context( { 'deviceList':deviceList} )
    #    return HttpResponse(t.render(c))
    #
    return render_to_response('ttux/devices.html',
                              {'deviceList': deviceList})


def sso_login_view(request, device_name):
    key = request.GET.get('key', '1111')
    if key in API_KEYS:
        username = API_KEYS[key]
        user = get_object_or_404(User, username=username)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return HttpResponseRedirect('/device/' + device_name)
    else:
        return HttpResponse('Not Authorized')


@csrf_exempt
def initialize_device(request):
    """
    Step one in app authentication process
    :param request:
    :return:
    """
    if request.method == "POST":
        data = JSONParser().parse(request)
        payload = InitializeSerializer(data=data)

        if payload.is_valid():
            api_key = payload.data.get('api_key')
            if api_key in API_KEYS:
                username = API_KEYS[api_key]
                user = get_object_or_404(User, username=username)

            # TODO: Find out logic for add user to groups
            group = user.groups.first()
            device_name = payload.data.get('email')

            cam, created = mobileCam.objects.get_or_create(
                name=device_name,
                email=payload.data.get('email'),
                defaults=dict(
                    first_name=payload.data.get('firstName'),
                    last_name=payload.data.get('lastName'),
                    phone_number=payload.data.get('phoneNumber'),
                    groups=group,
                )
            )

            session = Session.get(device_name)
            if session is None:
                Session.put(device_name, Session())

            return JsonResponse({'status': 'OK', 'device_name': cam.name})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/?next=%s' % request.path)
