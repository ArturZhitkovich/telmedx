# DJ session handler

import gevent.queue
#import logging
#logger = logging.getLogger("session");

from util.queue import DiscardingQueue

class Session(object):
    REGISTRY = {}
    
    def __init__(self):
        self.commands = gevent.queue.Queue(4)
        self.control_greenlet = None
        self.fragments = {}
        self.sequence_number = None
        self.viewers = {}
        
        print("__init__ finished")
  
    # get the most recent frame
    def get_lastFrame(self):
#        logger.info("get_lastFrame")
        return self.lastFrame;
    
    def set_lastFrame(self, frame):
#        logger.info("set_lastFrame")
        self.lastFrame = frame
        for queue in self.viewers.values():
            queue.put(frame)
        
    def add_viewer(self, address):
        return self.viewers.setdefault(address, DiscardingQueue(4))
        #NOTE: setdefault() is like get(), except that if k is missing, x is both returned and inserted into the dictionary as the value of k. x defaults to None.
        #NOTE: http://docs.python.org/release/2.5.2/lib/typesmapping.html 
    
    def enqueue_frame(self, frame):
            # ship off to any listeners out there 
            for queue in self.viewers.values():
                queue.put(frame)        
    
    def enqueue_frame_fragment(self, payload, sequence_number, count, index):
        if sequence_number != self.sequence_number:
            self.sequence_number = sequence_number
            self.fragments = {}

        self.fragments[index] = payload
        
        if len(self.fragments) == count:
            #self.lastFrame = self.newFrame;
            # we have all of the fragments now

            # join them together
            frame = "".join((self.fragments[i] for i in range(count)))

            # write to a file
            # TODO: to speed this up, move it to a seperate listener so it does not slow things down
            #f=open("lastFrame.jpg", "wb+")
            #f.write(frame)
            #f.close()
#            logger.info("** updating Last Frame");
            #self.lastFrame = frame.copy(); # in memory copy of the last frame
            self.lastFrame = frame;
            
            # ship off to any listeners out there 
            for queue in self.viewers.values():
                queue.put(frame)
                
    @staticmethod
    def get(key):
        return Session.REGISTRY.get(key)

    @staticmethod
    def put(key, session):
        Session.REGISTRY[key] = session
        
    def remove_viewer(self, address):
        self.viewers.pop(address, None)
    
    
