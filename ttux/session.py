#################################################################################
# @file session.py
# @brief  phone/browser session controller
# @author Tereus Scott
# Creation Date  Sept 28, 2011
# Copyright 2013 telmedx
#  
# Major Revision History
#    Date          Author          Description
#################################################################################
 
import gevent.queue
import logging
logger = logging.getLogger("session");

from util.queue import DiscardingQueue

class Session(object):
    REGISTRY = {}
    
    
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        logger.info("session:__init__")
#        self.commandQ = gevent.queue.Queue(1)
#        self.snapshotQ = gevent.queue.Queue(1)
#        self.control_greenlet = None
#        #self.fragments = {}
#        self.sequence_number = None
#        self.viewers = {}

####################################################################################
# Session instance Methods for a specific device
####################################################################################

    # add a video stream viewer for this specific device session instance
    # create a discarding queue, add it to self.viwerers and return a handle to that queue.
    def add_viewer(self, address):
        logger.info("add_viewer address:" + address)
        return self.viewers.setdefault(address, DiscardingQueue(4))
        #NOTE: setdefault() is like get(), except that if k is missing, x is both returned and inserted into the dictionary as the value of k. x defaults to None.
        #NOTE: http://docs.python.org/release/2.5.2/lib/typesmapping.html
    #def 


    # add a video sream frame to a specific device session instance
    # this frame will be broadcast to all viewers via their queues.
    def enqueue_frame(self, frame):
        logger.info("enqueue_frame")
        # ship off to any listeners out there 
        for queue in self.viewers.values():
            queue.put(frame)
        # save the last frame
        self.LastFrame = frame
        self.frameNumber += 1 
    #def

    def get_frameNumber(self):
        return self.frameNumber
    
    def get_lastFrame(self):
        return self.LastFrame

    def clear_lastFrame(self):
        self.LastFrame = ""

    # remove a viewer from a specific device session instance 
    def remove_viewer(self, address):
        logger.info("remove_viewer address:" + address)
        self.viewers.pop(address, None)
    #def


##########################################################################################
# Static Methods
##########################################################################################

    # get Session instance for a given device (key)
    @staticmethod
    def get(key):
        logger.info("get key:" + str(key))
        return Session.REGISTRY.get(key)


    # add a session for a device name (key), but only add it 
    # if there is not already a session for this device.
    # this is called at startup to initialize the session objects
    # for each device.
    @staticmethod
    def put(key, session):
        logger.info("put key: " + str(key) )
        print "REGISTRY before:"
        for k in Session.REGISTRY:
            print "   k: " + k
        print "Checking for key in REGISTRY"
        if key in Session.REGISTRY:
            print "key found: " + key
        else:
            Session.REGISTRY[key] = session
            session.commandQ = gevent.queue.Queue(1)
            session.snapshotQ = gevent.queue.Queue(1)
            session.control_greenlet = None
            session.sequence_number = None
            session.viewers = {}
            session.LastFrame = "" # store the most recently received frame here?
            session.frameNumber = 0 # frame number of the most recent frame
        #END if
                
        print "REGISTRY after:"
        for k in Session.REGISTRY:
            print "   k: " + k

