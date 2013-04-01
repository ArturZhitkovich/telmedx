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
        self.assertTrue(True) 
        return
        #DONE#
    
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
        self.assertTrue(True) 
        return
        #DONE#
    
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
        print "got OTUK:" + response['OTUK']
        deviceName = response['OTUK']
        
        # register Ticket and get SUID
        response = c.get('/ttux/registerKey/' + deviceName)
        print("status: expect 200, got:" + str(response.status_code) )
        self.assertTrue(response.status_code == C.HSTAT_OK)
        #SUID = response['SUID']
        #print("got SUID: " + SUID)
        # decode json response
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
        self.assertTrue(True) 
        return
        #DONE#
        
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
         
        
    # Test: generate the maximum number of sessions and verify we get an error after the last slot is used up
    def test_maxSessions(self):
        # skip this test
        #self.assertTrue(True) 
        #return
    
        print("unit test: test_maxSessions")
        c = Client()
        response=c.post('/login/', {'username': self.TEST_USER_ID, 'password':self.TEST_USER_PASS})
        self.assertTrue(response.status_code == C.HSTAT_LOGIN_SUCCESS)
        #print("expect 302, got:" + str(response.status_code) )
        
        #response=c.get('/ttux/deviceList')
        #print("status: expect 200, got:" + str(response.status_code) )
        #print(response)
        
        for i in range(1,13):
            print("Test makeNewSession: " + str(i))
            response = c.get('/ttux/makeNewSession')
            self.assertTrue(response.status_code == C.HSTAT_OK)
            #print("status: expect 200, got:" + str(response.status_code) )
            #print( response)
            #headers = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", response))
            print "KEY IS:" + response['OTUK']
            OTUKey = response['OTUK']
            print("Test: registerKey")
            
            response = c.get('/ttux/registerKey/' + OTUKey)
            self.assertTrue(response.status_code == C.HSTAT_OK)
            print("status: expect 200, got:" + str(response.status_code) )
            print(response)
        #END for
        
        sleep(5)
        print("Session list before timeout")
        Session.printSessionList()
        sleep(1)
        print("Session list after timeout")
        # print out list of sessions, after the timeout we should not have any left
        Session.printSessionList()
        
        #cleanup
        Session.removeAllSessions()
        Session.printSessionList()
        
        self.assertTrue(True)
    #END
#END 

if __name__ == '__main__':
    print("Session Unit Tests")

    unittest.main()

    print("Done.")
#END __main__
