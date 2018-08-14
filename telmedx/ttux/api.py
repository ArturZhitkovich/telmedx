import json
import logging

from django.http import HttpResponse, JsonResponse
from gevent.queue import Full
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins import TelmedxAPIView
from .session import Session

__all__ = (
    'PingAPIView',
    'FlashlightAPIView',
    'FlipCameraAPIView',
    'SnapshotAPIView',
)

FLASHLIGHT_STATUS_ON = 'on'
FLASHLIGHT_STATUS_OFF = 'off'

logger = logging.getLogger(__name__)


class PingAPIView(TelmedxAPIView):
    """
    API view that responds with the functionality that's available for the
    app version specified.
    """

    def get(self, request, app_version=None, format=None):
        device_name = str(self.request.user.uuid)

        # Has flip camera & flashlight
        if app_version == '1.0.0':
            session = Session.get(device_name)
            if session is None:
                Session.put(device_name, Session())
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
                except Full:
                    # remove item if the queue is blocked to keep stale
                    # requests from sitting in the queue
                    session.deviceSpecQ.get_nowait()
                except Exception as e:
                    # remove item if the queue is blocked to keep stale
                    # requests from sitting in the queue
                    session.deviceSpecQ.get_nowait()

        return Response({
            'data': 'pong'
        })


class FlashlightAPIView(TelmedxAPIView):
    def post(self, request, status=None, format=None):
        """
        Receive flashlight response from the phone/mobile device
        :param request:
        :param device_name:
        :param statust
        :return:
        """
        device_name = self.get_device_name(request)
        # status = None
        print("got flashlight from device: {}, {}".format(device_name, status))

        session = Session.get(device_name)

        try:
            session.flashlightQ.put_nowait(status)
        except:
            # logger.error("failed to queue up snapshot response")
            print("failed to queue up flashlight response from " + device_name.uuid)
            session.flashlightQ.get_nowait()  # empty the queue if full
            session.flashlightQ.put_nowait(status)

        return Response({'status': 'flashlightResponse'})


class SnapshotAPIView(TelmedxAPIView):
    def post(self, request, format=None):
        """
        receive snapshot response from the phone
        :param request:
        :param device_name:
        :return:
        """
        device_name = self.get_device_name(request)
        image = request.read()

        session = Session.get(device_name)
        try:
            session.snapshotQ.put_nowait(image)
            session.add_snapshot_count()
        except:
            # logger.error("failed to queue up snapshot response")
            # print("failed to queue up snapshot response from " + device_name)
            session.snapshotQ.get_nowait()  # empty the queue if full
            session.snapshotQ.put_nowait(image)
            session.add_snapshot_count()
        # END

        return Response({'status': 'snapshot_response'})

class FlipCameraAPIView(TelmedxAPIView):
    def post(self, request, status=None, format=None):
        """
        Receive flip camera response from phone/device
        :param request:
        :param device_name:
        :param status:
        :return:
        """
        session = Session.get(request.user)

        try:
            session.flipcameraQ.put_nowait(status)
        except:
            # logger.error("failed to queue up snapshot response")
            print("failed to queue up snapshot response from " + request.user.uuid)
            session.flipcameraQ.get_nowait()  # empty the queue if full
            session.flipcameraQ.put_nowait(status)

        return HttpResponse('flipcameraResponse')


class ReceivedImageAPIView(APIView):
    def post(self, request, device_name=None):
        """
        Receive image data from mobile apps.
        This assumes data is sent through in binary mode.

        If there is a command in the queue (from the web app), this command
        will be sent as a response.

        Example `curl` command:
        ```bash
        curl -X POST --data-binary localhost:8000/ttux/img/user@example.com/img0001.jpg
        ```

        :param request:
        :param device_name:
        :return:
        :rtype: HttpResponse
        """
        if not device_name:
            session = Session.get(request.user)
        else:
            session = Session.get(device_name)

        if not session:
            return Response({'status': 'Not ready'})

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
            logger.info("sending command to the phone: %s", command_resp)

        # ENDIF
        ##return HttpResponse(status="200 OK")
        return JsonResponse({'command': command_resp})


class SnapshotResponseAPIView(APIView):
    def post(self, request, device_name=None):
        """
        receive snapshot response from the phone
        :param request:
        :param device_name:
        :return:
        """
        # print("got snapshot response from device: " + device_name)
        if not device_name:
            session = Session.get(request.user)
        else:
            session = Session.get(device_name)

        image = request.read()

        try:
            session.snapshotQ.put_nowait(image)
            session.add_snapshot_count()
        except:
            # logger.error("failed to queue up snapshot response")
            # print("failed to queue up snapshot response from " + device_name)
            session.snapshotQ.get_nowait()  # empty the queue if full
            session.snapshotQ.put_nowait(image)
            session.add_snapshot_count()
        # END

        return HttpResponse({'status': 'snapshot_response'})
