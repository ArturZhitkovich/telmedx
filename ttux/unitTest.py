'''
Session unit test
Created on 2013-03-29

@author: Tereus Scott
'''
from django.test.client import Client
from time import sleep
from ttux.session import Session


#Test: send an image with no active session, verify handling of bad SUID
def test_imageReceive_noSession():
    print("unit test: receive an image for an invalid OTUK")
    
    #setup
    Session.removeAllSessions()
    c = Client()

    #test
    response=c.post('/ttux/img/badDeviceName/img1234.jpg', data = "this is not an image", content_type='img/jpeg')
    print("response: status: " + str(response.status_code) )
    #TODO add verification of status code
    print response
#END test_imageReceive

#Test: send an image with a valid SUID
def test_imageReceive_success():
    print("unit test: post an image for a valid SUID")
    
    #setup
    Session.removeAllSessions()
    c = Client()
    response=c.post('/login/', {'username':'developer', 'password':'rootroot'})
    print("login: expect 302, got:" + str(response.status_code) )

    #test
    
    #get a ticket
    print("Get ticket")
    response = c.get('/ttux/makeNewSession')
    print("status: expect 200, got:" + str(response.status_code) )
    print "got OTUK:" + response['OTUK']
    deviceName = response['OTUK']
    
    # register Ticket and get SUID
    response = c.get('/ttux/registerKey/' + deviceName)
    print("status: expect 200, got:" + str(response.status_code) )
    print(response)
    SUID = response['SUID']
    print("got SUID: " + SUID)
            
    # send image
    print("sending image")
    response=c.post('/ttux/img/' + SUID + '/img1234.jpg', data = "this is not an image", content_type='img/jpeg')
    print("response: status: " + str(response.status_code) )
    print response
    #TODO check response content - see design doc for possible response codes
    
#END test_imageReceive

# Test: verify handling of invalid OTUK
def test_invalidTicket():
    print("unit test: invalid ticket")
    
    # setup
    Session.removeAllSessions()
    c = Client()
    response=c.post('/login/', {'username':'developer', 'password':'rootroot'})
    print("login: expect 302, got:" + str(response.status_code) )
    
    # start test
    # the registry is empty now, try to register an invalid OTUK
    print("try to send an invalid key")
    response = c.get('/ttux/registerKey/' + "9876")
    print response
    print("response: status: " + str(response.status_code) )
    
    print("unit test: invalid ticket: Done")
#END test_invalidTickey
     
    
# Test: generate the maximum number of sessions and verify we get an error after the last slot is used up
def test_maxSessions():
    print("unit test: test_maxSessions")
    c = Client()
    response=c.post('/login/', {'username':'developer', 'password':'rootroot'})
    print("expect 302, got:" + str(response.status_code) )
    
    #response=c.get('/ttux/deviceList')
    #print("status: expect 200, got:" + str(response.status_code) )
    #print(response)
    
    for i in range(1,13):
        print("Test makeNewSession: " + str(i))
        response = c.get('/ttux/makeNewSession')
        print("status: expect 200, got:" + str(response.status_code) )
        #print( response)
        #headers = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", response))
        print "KEY IS:" + response['OTUK']
        OTUKey = response['OTUK']
        print("Test: registerKey")
        response = c.get('/ttux/registerKey/' + OTUKey)
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
#END    

if __name__ == '__main__':
    print("Session Unit Tests")
    
    test_imageReceive_success()    
    # test_imageReceive_noSession()
    # test_maxSessions()
    # test_invalidTicket()
    
    print("Done.")
#END __main__
