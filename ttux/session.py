# DJ session handler

import gevent.queue
import logging
logger = logging.getLogger("session");

from util.queue import DiscardingQueue

class Session(object):
    REGISTRY = {}
    
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        logger.info("session:__init__")
        self.commands = gevent.queue.Queue(4)
        self.control_greenlet = None
        self.fragments = {}
        self.sequence_number = None
        self.viewers = {}

#    # get the most recent frame
#    def get_lastFrame(self):
##        logger.info("get_lastFrame")
#        return self.lastFrame;
    
#    def set_lastFrame(self, frame):
##        logger.info("set_lastFrame")
#        self.lastFrame = frame
#        for queue in self.viewers.values():
#            queue.put(frame)
        
    def add_viewer(self, address):
        logger.info("add_viewer address:" + address)
        return self.viewers.setdefault(address, DiscardingQueue(4))
        #NOTE: setdefault() is like get(), except that if k is missing, x is both returned and inserted into the dictionary as the value of k. x defaults to None.
        #NOTE: http://docs.python.org/release/2.5.2/lib/typesmapping.html 


    def enqueue_frame(self, frame):
        logger.info("enqueue_frame")
        # ship off to any listeners out there 
        for queue in self.viewers.values():
            queue.put(frame)        


    @staticmethod
    def get(key):
        logger.info("get key:" + str(key))
        return Session.REGISTRY.get(key)


    @staticmethod
    def put(key, session):
        logger.info("put key: " + str(key) )
        print "REGISTRY before:"
        for k in Session.REGISTRY:
            print "   k: " + k
        print "Cheking for key in REGISTRY"
        if key in Session.REGISTRY:
            print "key found: " + key
        else:
            Session.REGISTRY[key] = session
        
        print "REGISTRY after:"
        for k in Session.REGISTRY:
            print "   k: " + k
        
    def remove_viewer(self, address):
        logger.info("remove_viewer address:" + address)
        self.viewers.pop(address, None)
    
    
