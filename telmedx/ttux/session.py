import datetime
import logging
import time

import gevent.queue
from django.contrib.auth import get_user_model

from util.queue import DiscardingQueue
from .models import sessionLog, MobileCam

logger = logging.getLogger(__name__)
User = get_user_model()


class Session:
    """
    This class is an in-app/in-memory cache that keeps track of frames from
    the user camera and sends them to the web interface.
    """
    REGISTRY = {}
    commandQ = gevent.queue.Queue(1)
    snapshotQ = gevent.queue.Queue(1)
    flashlightQ = gevent.queue.Queue(1)
    flipcameraQ = gevent.queue.Queue(1)
    deviceSpecQ = gevent.queue.Queue(1)
    begin_timestamp = 0
    last_frame_timestamp = 0
    frames_in_session = 0
    captured_images = 0
    control_greenlet = None
    sequence_number = None
    device_name = None
    viewers = {}
    LastFrame = ""  # store the most recently received frame here?
    frameNumber = 0  # frame number of the most recent frame
    key = None

    def __init__(self, key=None):
        logging.basicConfig(level=logging.DEBUG)
        logger.info("session:__init__")
        self.key = key

    # add a video stream viewer for this specific device session instance
    # create a discarding queue, add it to self.viwerers and return a handle to that queue.
    def add_viewer(self, address):
        logger.info("add_viewer address:" + address)
        return self.viewers.setdefault(address, DiscardingQueue(4))
        # NOTE: setdefault() is like get(), except that if k is missing, x is both returned and inserted into the dictionary as the value of k. x defaults to None.
        # NOTE: http://docs.python.org/release/2.5.2/lib/typesmapping.html

    # def

    def add_snapshot_count(self):
        self.captured_images += 1

    # add a video sream frame to a specific device session instance
    # this frame will be broadcast to all viewers via their queues.
    def enqueue_frame(self, frame):
        # ship off to any listeners out there
        for queue in self.viewers.values():
            queue.put(frame)
        # save the last frame
        self.LastFrame = frame
        self.frameNumber += 1
        self.frames_in_session += 1
        if self.begin_timestamp == 0:
            self.begin_timestamp = time.time()
        if not self.last_frame_timestamp == 0 and time.time() - self.last_frame_timestamp > 5:
            self.log_session()
        self.last_frame_timestamp = time.time()

    def clean_session(self):
        if not self.last_frame_timestamp == 0 and time.time() - self.last_frame_timestamp > 5:
            self.log_session()

    def log_session(self):
        if self.last_frame_timestamp - self.begin_timestamp > 2:
            cam = MobileCam.objects.get(user__uuid=self.device_name)
            log = sessionLog()
            log.device = cam
            log.begin_timestamp = datetime.datetime.fromtimestamp(self.begin_timestamp)
            log.end_timestamp = datetime.datetime.fromtimestamp(self.last_frame_timestamp)
            log.frames = self.frames_in_session
            log.captured_images = self.captured_images
            log.save()
        self.last_frame_timestamp = 0
        self.begin_timestamp = 0
        self.frames_in_session = 0
        self.captured_images = 0

    def get_frameNumber(self):
        return self.frameNumber

    def get_lastFrame(self):
        return self.LastFrame

    def clear_lastFrame(self):
        self.LastFrame = ""

    def remove_viewer(self, address):
        """
        remove a viewer from a specific device session instance
        :param address:
        :return:
        """
        logger.info("remove_viewer address:" + address)
        self.viewers.pop(address, None)

    @staticmethod
    def get_queue():
        return gevent.queue.Queue(1)

    @staticmethod
    def get(key):
        """
        get `Session` instance for a given device (key).
        :param key: Typically a device name, or User
        :return:
        """
        if isinstance(key, User) and getattr(key, 'uuid'):
            key = str(key.uuid)
        return Session.REGISTRY.get(key)

    @staticmethod
    def put(key, session):
        """
        add a session for a device name (key), but only add it
        if there is not already a session for this device.
        this is called at startup to initialize the session objects
        for each device.
        :param key:
        :param session:
        :type session: Session
        :return:
        """
        if isinstance(key, User) and getattr(key, 'uuid'):
            key = str(key.uuid)

        if key not in Session.REGISTRY:
            Session.REGISTRY[key] = session
            session.commandQ = gevent.queue.Queue(1)
            session.snapshotQ = gevent.queue.Queue(1)
            session.flashlightQ = gevent.queue.Queue(1)
            session.flipcameraQ = gevent.queue.Queue(1)
            session.deviceSpecQ = gevent.queue.Queue(1)
            session.device_name = str(key)
            session.begin_timestamp = 0
            session.last_frame_timestamp = 0
            session.frames_in_session = 0
            session.captured_images = 0
            session.control_greenlet = None
            session.sequence_number = None
            session.viewers = {}
            # store the most recently received frame here?
            session.LastFrame = ""
            # frame number of the most recent frame
            session.frameNumber = 0

        logger.debug("REGISTRY after:")
        for k in Session.REGISTRY:
            logger.debug("   k: " + k)
