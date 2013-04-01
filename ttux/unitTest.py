'''
Session unit test
Created on 2013-03-29

@author: Tereus Scott
'''
from django.test.client import Client
from time import sleep
from ttux.session import Session
import unittest
import ttux_constants as C
import json

class TestSessionKeys(unittest.TestCase):
    
    # Test Case Constants
    TEST_IMG_DATA      = "this is a jpg image" # some data to send in place of a jpg image
    TEST_USER_ID       = "developer"
    TEST_USER_PASS     = "rootroot"
    
    
    ###########################################################################################
    # Test setup and teardown - these are run for each individual test below
    ###########################################################################################
    def setUp(self):
        #print("\n** Start test")
        #put any global test setup steps here
        Session.removeAllSessions()
    #END
    
    def tearDown(self):
        #print("\n** End Test")
        #put any global test tear-down steps here
        Session.removeAllSessions()
    #END
    
    ###########################################################################################
    # Tests
    ###########################################################################################
    
    #Test: send an image with no active session, verify handling of bad SUID
    def test_imageReceive_noSession(self):
        # skip this test
        #self.assertTrue(True) 
        #return
    
        print("unit test: receive an image for an invalid OTUK")
        
        c = Client()
        response=c.post('/ttux/img/badDeviceName/img1234.jpg', data = self.TEST_IMG_DATA, content_type='img/jpeg')
        #print(" status: " + str(response.status_code) )
        self.assertTrue( response.status_code == C.HSTAT_AUTH_FAIL)
        print("response:" + str(response.content))
        self.assertTrue( response.content == C.RC_BAD_SUID)
    #END test_imageReceive
    
    #Test: send an image with a valid SUID
    def test_imageReceive_success(self):
        # skip this test
        #self.assertTrue(True) 
        #return
    
        print("unit test: post an image for a valid SUID")
        
        c = Client()
        #response=c.post('/login/', {'username':'developer', 'password':'rootroot'})
        response=c.post('/login/', {'username': self.TEST_USER_ID, 'password':self.TEST_USER_PASS})
        #print("login: expect 302, got:" + str(response.status_code) )
        self.assertTrue(response.status_code == C.HSTAT_LOGIN_SUCCESS)
        #test
        
        #get a ticket
        print("Get ticket")
        response = c.get('/ttux/makeNewSession')
        self.assertTrue(response.status_code == C.HSTAT_OK)
        self.assertTrue(response['Content-Type'] == "application/json")
        resp_data = json.loads( response.content )
        self.assertTrue( 'OTUK' in resp_data[0] )
        self.assertTrue( resp_data[0]['result'] == C.RC_SESSION_OK )
        # verify that the OTUK is not empty
        self.assertTrue( len(resp_data[0]['OTUK']) != 0 )
        deviceName = resp_data[0]['OTUK']
        print "KEY IS: " + deviceName
                
#        print "got OTUK:" + response['OTUK']
#        deviceName = response['OTUK']
        
        # register Ticket and get SUID
        response = c.get('/ttux/registerKey/' + deviceName)
        print("status: expect 200, got:" + str(response.status_code) )
        self.assertTrue(response.status_code == C.HSTAT_OK)
        self.assertTrue(response['Content-Type'] == "application/json")
        resp_data = json.loads( response.content )
        self.assertTrue( resp_data[0]['result'] == C.RC_REGISTER_OK )
        # verify that the SUID element was returned
        self.assertTrue( 'SUID' in resp_data[0] )
        # verify that the SUID is not empty
        self.assertTrue( len(resp_data[0]['SUID']) != 0 )
        SUID = resp_data[0]['SUID']
        print("got SUID: " + SUID)
        
        # send image
        print("sending image")
        response=c.post('/ttux/img/' + SUID + '/img1234.jpg', data = "this is not an image", content_type='img/jpeg')
        self.assertTrue(response.status_code == C.HSTAT_OK)
    #END test_imageReceive

    
    # Test: verify handling of invalid OTUK
    def test_invalidTicket(self):
        # skip this test
        #self.assertTrue(True) 
        #return
        
        print("unit test: invalid ticket")
        
        c = Client()
        response=c.post('/login/', {'username': self.TEST_USER_ID, 'password':self.TEST_USER_PASS})
        self.assertTrue(response.status_code == C.HSTAT_LOGIN_SUCCESS)
        
        # the registry is empty now, try to register an invalid OTUK
        print("try to send an invalid key")
        response = c.get('/ttux/registerKey/' + "9876")
        print response
        print("response: status: " + str(response.status_code) )
        self.assertTrue( response.status_code == C.HSTAT_OK, "expected status:" + str(C.HSTAT_OK) + " got status:" + str(response.status_code) )
        self.assertTrue(response['Content-Type'] == "application/json")
        resp_data = json.loads( response.content )
        self.assertTrue( resp_data[0]['result'] == C.RC_REGISTER_FAIL )
        # verify that the SUID element was returned
        self.assertTrue( 'SUID' in resp_data[0] )
        # verify that the SUID is empty
        self.assertTrue( len(resp_data[0]['SUID']) == 0 )
        
        print("unit test: invalid ticket: Done")
    #END test_invalidTickey
         
        
    # Test: generate the maximum number of sessions and verify we get an error after the last 
    # slot is used up
    def test_maxSessions(self):
        # skip this test
        #self.assertTrue(True) 
        #return
    
        print("unit test: test_maxSessions")
        
        # set up smaller session defaults for testing
        Session.SESSION_TIMEOUT=30
        Session.OTUK_TIMEOUT=10
        Session.OTUK_MIN_RANGE=1000
        Session.OTUK_MAX_RANGE=1010
        
        c = Client()
        response=c.post('/login/', {'username': self.TEST_USER_ID, 'password':self.TEST_USER_PASS})
        self.assertTrue(response.status_code == C.HSTAT_LOGIN_SUCCESS)
        
        for i in range(Session.OTUK_MIN_RANGE, Session.OTUK_MAX_RANGE):
            print("Test makeNewSession: " + str(i))
            response = c.get('/ttux/makeNewSession')
            self.assertTrue(response.status_code == C.HSTAT_OK)
            self.assertTrue(response['Content-Type'] == "application/json")
            resp_data = json.loads( response.content )
            self.assertTrue( 'OTUK' in resp_data[0] )
            self.assertTrue( resp_data[0]['result'] == C.RC_SESSION_OK )
            # verify that the OTUK is not empty
            self.assertTrue( len(resp_data[0]['OTUK']) != 0 )
            OTUKey = resp_data[0]['OTUK']
            print "KEY IS: " + OTUKey
        #END for
        
        # Try to add one more
        print("Test makeNewSession when all keys are used up")
        response = c.get('/ttux/makeNewSession')
        self.assertTrue(response.status_code == C.HSTAT_NO_KEYS_LEFT)
        resp_data = json.loads( response.content )
        self.assertTrue( resp_data[0]['result'] == C.RC_SESSION_FAIL )
        # verify that the OTUK is not empty
        self.assertTrue( resp_data[0]['OTUK'] == "0000" )
        
        print("Session list before timeout")
        Session.printSessionList()
        # Wait for all the keys to timeout        
        sleep(Session.OTUK_TIMEOUT)
        # now we should be able to create a new one
        response = c.get('/ttux/makeNewSession')
        self.assertTrue(response.status_code == C.HSTAT_OK)
        resp_data = json.loads( response.content )
        self.assertTrue( 'OTUK' in resp_data[0] )
        self.assertTrue( resp_data[0]['result'] == C.RC_SESSION_OK )
        # verify that the OTUK is not empty
        self.assertTrue( len(resp_data[0]['OTUK']) != 0 )
        OTUKey = resp_data[0]['OTUK']        
    #END


    # Test: verify that keys are cleared as soon as they are used to establish a connection to a
    # session.
    def test_sessionKeyReuse(self):
        # skip this test
        #self.assertTrue(True) 
        #return
        print("unit test: test_sessionKeyReuse")
        
        # set up smaller session defaults for testing
        Session.SESSION_TIMEOUT=30
        Session.OTUK_TIMEOUT=10
        Session.OTUK_MIN_RANGE=1000
        Session.OTUK_MAX_RANGE=1010
        
        c = Client()
        response=c.post('/login/', {'username': self.TEST_USER_ID, 'password':self.TEST_USER_PASS})
        self.assertTrue(response.status_code == C.HSTAT_LOGIN_SUCCESS)
        
        # loop for five more than the maximum number of elements in the range
        # this will ensure that each ticket gets cleared when it is registered
        # and is available for reuse.
        SUID_list = []
        for i in range(Session.OTUK_MIN_RANGE, Session.OTUK_MAX_RANGE + 5 ):
            print("Test makeNewSession: " + str(i))
            response = c.get('/ttux/makeNewSession')
            self.assertTrue(response.status_code == C.HSTAT_OK)
            self.assertTrue(response['Content-Type'] == "application/json")
            resp_data = json.loads( response.content )
            self.assertTrue( 'OTUK' in resp_data[0] )
            self.assertTrue( resp_data[0]['result'] == C.RC_SESSION_OK )
            # verify that the OTUK is not empty
            self.assertTrue( len(resp_data[0]['OTUK']) != 0 )
            OTUKey = resp_data[0]['OTUK']
            print "KEY IS: " + OTUKey

            print("Test: registerKey")
            # register Ticket and get SUID
            response = c.get('/ttux/registerKey/' + OTUKey)
            self.assertTrue(response.status_code == C.HSTAT_OK)
            self.assertTrue(response['Content-Type'] == "application/json")
            resp_data = json.loads( response.content )
            self.assertTrue( resp_data[0]['result'] == C.RC_REGISTER_OK )
            # verify that the SUID element was returned
            self.assertTrue( 'SUID' in resp_data[0] )
            # verify that the SUID is not empty
            self.assertTrue( len(resp_data[0]['SUID']) != 0 )
            SUID = resp_data[0]['SUID']
            self.assertTrue( SUID != "0000" )
            print("got SUID: " + resp_data[0]['SUID'] )
            self.assertFalse(SUID in SUID_list)
            SUID_list.append(SUID)
            print ("SUID list" + str(SUID_list))
        #END for
        
        # verify session timeout. All sessions should be deleted after SESSION_TIMEOUT
        print("Session list before timeout")
        Session.printSessionList()
        print("Number of sessions active: " + str( len( Session.REGISTRY) ) )
        sleep(Session.SESSION_TIMEOUT)
        print("Number of sessions active: " + str( len( Session.REGISTRY) ) )
        self.assertTrue( len( Session.REGISTRY) == 0)
    #END
    
#END class

if __name__ == '__main__':
    print("Session Unit Tests")

    unittest.main()

    print("Done.")
#END __main__
