#################################################################################
# @file session.py
# @brief  phone/browser session controller
# @author Tereus Scott
# Creation Date  Sept 28, 2011
# Copyright 2013 telmedx
#  
# Major Revision History
#    Date         Version     Author          Description
#    2011         1.0.0       Matt Green      initial implementation
#    July 2012    1.0.1       Tereus Scott    Refactored: added support for single frames and control channel
#    March 2013   1.0.2       Tereus Scott    Added Ticket and key handling
#################################################################################

__version__ = '1.0.2'
"""Module session.py
   main session handler. This links the phone and the browser and 
   controls all aspects of the session
"""

# from util.timers import RepeatedTimer
from django.conf.urls.static import static
import gevent.queue
from util.queue import DiscardingQueue
import random
from util.telX_tokens import makeUniqueToken, makeOneTimeUseKey
import util.timers
from threading import Timer
from time import sleep

import logging
logger = logging.getLogger("session");
logging.basicConfig(level=logging.DEBUG)


class Session(object):
    REGISTRY = {}   # this is where we will store the list of sessions
    # general timeout for all sessions. This is to prevent stale sessions from hanging around forever on the server clogging up memory
    SESSION_TIMEOUT = (24 * 60 * 60)
    # Ticket timeout: the user has two minutes to enter the key for a new session
    OTUK_TIMEOUT = (2 * 60)
    # Maximum range for Tickets: (use this for unit testing so we can shorten the range to test boundary conditions)
    OTUK_MIN_RANGE = 1000
    OTUK_MAX_RANGE = 9999 
    
    # initialize this object
    def __init__(self):
        #logging.basicConfig(level=logging.DEBUG)
        #logging.basicConfig(level=logging.INFO)
        logger.info("session:__init__")
        # seed the random number generator with the current time
        random.seed()
    #def

    ####################################################################################
    # Session instance Methods for a specific device (instance)
    ####################################################################################
    def add_viewer(self, address):
        """ add a video stream viewer for this specific device session instance
        create a discarding queue, add it to self.viwerers and return a handle to that queue. 
        """
        logger.info("add_viewer address:" + address)
        return self.viewers.setdefault(address, DiscardingQueue(4))
        #NOTE: setdefault() is like get(), except that if k is missing, x is both returned and inserted into the dictionary as the value of k. x defaults to None.
        #NOTE: http://docs.python.org/release/2.5.2/lib/typesmapping.html
    #def 


    def enqueue_frame(self, frame):
        """add a video stream frame to a specific device session instance
        this frame will be broadcast to all viewers via their queues."""
        logger.info("enqueue_frame")
        # ship off to any listeners out there 
        for queue in self.viewers.values():
            queue.put(frame)
        # save the last frame
        self.LastFrame = frame
        self.frameNumber += 1 
    #def

    def get_frameNumber(self):
        """get the frame number of the current video frame stored for this session instance"""
        return self.frameNumber
    #def
    
    def get_lastFrame(self):
        """get the most recent frame for this session instance"""
        return self.LastFrame
    #def

    def clear_lastFrame(self):
        """remove the most recent frame for this session instance"""
        self.LastFrame = ""
    #def

    def remove_viewer(self, address):
        """remove a viewer from a specific device session instance"""
        logger.info("remove_viewer address:" + address)
        self.viewers.pop(address, None)
    #def
    

    ##########################################################################################
    # Static Methods
    ##########################################################################################
    @staticmethod
    def get_SUID(oneTimeKey):
        """find session that has the oneTimeKey, return it's SUID and invalidate the oneTimeKey"""
        logger.debug("searching for key:" + oneTimeKey)
        SUID="none"
        for k in list(Session.REGISTRY):
            try:
                s = Session.REGISTRY.get(k)
                logger.debug( "OTUK: " + s.oneTimeKey + " SUID: " + s.SUID )
                if oneTimeKey == s.oneTimeKey:
                    logger.debug("    Found it")
                    SUID = s.SUID
                    s.oneTimeKey="0000" #clear the OTUK after first use
                    s.oneTimeKey_timer.cancel()
                    return SUID
            except(KeyError):
                logger.debug("k: " + k + " was removed while we were searching the registry")
                pass
        #END for
        return SUID
    #END get_SUID 
    
    @staticmethod
    def removeSession_callback(s):
        logger.info("timeout triggered on session SUID:" + s.SUID + ", removing this session from the REGISTRY list")
        try:
            Session.REGISTRY.pop(s.SUID)
        except:
            logger.error("Unable to remove SUID:" + s.SUID + " from REGISTRY")
    #END removeSession_callback
    
    @staticmethod
    def removeOTUK_callback(s):
        logger.info("timeout triggered on session OTUK: " + s.oneTimeKey + ", Key has not been used, removing this session from the REGISTRY list")
        logger.info("SUID: " + s.SUID)
        if s.oneTimeKey == "0000":
            logger.warning("OTUK is already in use, clearing the session anyway")
        try:
            Session.REGISTRY.pop(s.SUID)
        except:
            logger.error("Unable to remove OTUK: " + s.oneTimeKey + " from REGISTRY")
    #END removeOTUK_callback
    
    @staticmethod
    def makeSession(request):
        """make a new session for a given authenticated user
        This will create a new session object and assign a new OTUkey (one time use key).
        The OTUKey is returned to the caller and should be displayed to the user. This
        key will be entered at the phone and will be used in the get_SUID() call above to get the long token that will be 
        used for the rest of the transaction.
        This method must:
            - generate a unique OTUKey (generate a random value then make sure it is not already in use)
            - generate and store the SUID
            - store the user name (this might be useful later)
            - start a timer to invalidate the OTUKey after some small period of time (2-3 minutes?)
        """
       
        # get a set of the current set of active keys
        logger.debug("Keys in use:")
        OTUkeysInUse = set();
        for k in list(Session.REGISTRY):
            try:
                s = Session.REGISTRY.get(k)
                logger.debug( "    k: " + s.oneTimeKey)
                if s.oneTimeKey != "0000":
                    OTUkeysInUse.add( int(s.oneTimeKey) )
            except(KeyError):
                # this will happen if a timer has come along and deleted this key from
                # the registry while we are in this method
                logger.debug("k: " + k + " is no longer in the registry, skipping")
                pass
        #END for
        
#        logger.debug( "** TEST **")
#        logger.debug( set(range(1000,1010)) )
#        logger.debug( OTUkeysInUse )
#        logger.debug( "** END TEST **" )
        
        #OTUKey = str(random.sample( set( range(1000, 9999)) - OTUkeysInUse, 1)[0])
        population= set( range(Session.OTUK_MIN_RANGE, Session.OTUK_MAX_RANGE)) - OTUkeysInUse
        logger.debug("keys left: ")
        logger.debug( population )
        if len(population) <= 0:
            logger.error ("Error: no keys left")
            OTUKey="0000"
            raise LookupError
        else:
            OTUKey = str(random.sample( population, 1)[0])

        # make a new SUID, this will be the key value for our object
        # note that the user name and password are required, so this can only be called with an authenticated user
        key = makeUniqueToken(request)    
        
        logger.info("New OTUK: " + OTUKey + " SUID: " + key)
        
        # make a new session
        session=Session()
        Session.REGISTRY[key] = session
        session.commandQ = gevent.queue.Queue(1)    # queue used to send commands from the browser to the phone
        session.snapshotQ = gevent.queue.Queue(1)   # queue used to send the completed snapshot back from the phone to the browser
        session.control_greenlet = None
        session.sequence_number = None      
        session.viewers = {}                # list of client browsers who are viewing this session (not used right now, need to use this to be able to kill a session after all viewers are gone
        session.LastFrame = ""              # store the most recently received frame from the phone
        session.frameNumber = 0             # frame number of the most recent frame
        session.oneTimeKey = OTUKey         # four digit user session key, one time use to establish session with the phone
        session.SUID=key 
        
        # add timers
        # TODO set up constant or system defines for these timeouts, using 30 sec for testing
        # one time use key timeout, the phone has a short window of time to use the key, otherwise the session is removed.
        # TODO need to work out what the browser will do when the session goes away?
        session.oneTimeKey_timer = Timer(Session.OTUK_TIMEOUT, Session.removeOTUK_callback, [session] )  # one shot timer
        session.oneTimeKey_timer.start()
        
        # Global session timeout: this keeps sessions from running forever.
        #session.timer = RepeatedTimer(10, Session.removeSession_callback, session)
        session.removeSessiontimer = Timer(Session.SESSION_TIMEOUT, Session.removeSession_callback, [session] ) # one shot timer
        session.removeSessiontimer.start()
        return OTUKey
    #END makeSession
    


    @staticmethod
    def get(key):
        """static method: get Session instance for a given device (key)"""
        logger.info("get key:" + str(key))
        return Session.REGISTRY.get(key)
    #END get

    @staticmethod
    def put(key, session):
        """static method: add a session for a device name (key), but only add it 
        if there is not already a session for this device.
        this is called at startup to initialize the session objects
        for each device.
        """        
        logger.info("put key: " + str(key) )
        logger.debug("REGISTRY before:")
        for k in list(Session.REGISTRY):
            logger.debug( "   k: " + k)
        logger.debug( "Checking for key in REGISTRY")
        if key in Session.REGISTRY:
            logger.debug( "key found: " + key)
        else:
            Session.REGISTRY[key] = session
            session.commandQ = gevent.queue.Queue(1)    # queue used to send commands from the browser to the phone
            session.snapshotQ = gevent.queue.Queue(1)   # queue used to send the completed snapshot back from the phone to the browser
            session.control_greenlet = None
            session.sequence_number = None      
            session.viewers = {}                # list of client browsers who are viewing this session (not used right now, need to use this to be able to kill a session after all viewers are gone
            session.LastFrame = ""              # store the most recently received frame from the phone
            session.frameNumber = 0             # frame number of the most recent frame
            session.oneTimeKey = "1234"         # four digit user session key, one time use to establish session with the phone
            session.SUID="SUID bong"            # Session Unique Id, long hashed unique key, will live the duration of the session
        #END if
        logger.debug( "REGISTRY after:")
        for k in list(Session.REGISTRY):
            logger.debug( "   k: " + k)
    #END put

    @staticmethod
    def printSessionList():
        logger.debug("Session List:")
        for k in list(Session.REGISTRY):
            try:
                s = Session.REGISTRY.get(k)
            except(KeyError):
                pass
            logger.debug( "OTUK: " + s.oneTimeKey + " SUID: " + s.SUID)
    #END printSessionList
    
    
    # for unit testing support, remove all sessions
    @staticmethod
    def removeAllSessions():
        """Remove all currently active session and stop all timers. This is here to support
        unit testing. This should be called to clear all previous sessions prior to starting 
        a test case"""
         
        logger.info("removing all active sessions:")
        #NOTE: use list() to get a copy of the registry key list and iterate over that copy.
        # This is important because we are using timers which can fire at any time and delete an entry from the registry
        # if this happens while we are iterating through the registry we will get a runtime error complaining that
        # the size of the dictionary changed while were were iterating through it.
        for k in list(Session.REGISTRY):
            try:
                s = Session.REGISTRY.pop(k)
                s.oneTimeKey_timer.cancel()
                s.removeSessiontimer.cancel()
                logger.debug("popped k: " + k)
                logger.debug( "remove OTUK: " + s.oneTimeKey + " SUID: " + s.SUID)
            except(KeyError):
                logger.error("can't pop session k:" + k)
                pass #ignore this error
            sleep(1)     
#END class



# Unit Test Code
# TODO: refactor this out into separate unit test file and make use of django unit test runner?
if __name__ == '__main__':
    logger.info("unit test are in separate file")
