'''
Session unit test
Created on 2013-03-29

@author: Tereus Scott
'''
from django.test.client import Client
from time import sleep
from ttux.session import Session

#import re

if __name__ == '__main__':
    print("Session Unit Tests")
    c = Client()
    response=c.post('/login/', {'username':'developer', 'password':'rootroot'})
    print("expect 302, got:" + str(response.status_code) )
    
    #response=c.get('/ttux/deviceList')
    #print("status: expect 200, got:" + str(response.status_code) )
    #print(response)
    
    for i in range(1,10):
        print("Test makeNewSession")
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
        sleep(1)
    #END for
    
    sleep(5)
    print("Session list before timeout")
    Session.printSessionList()
    sleep(10)
    print("Session list after timeout")
    # print out list of sessions, after the timeout we should not have any left
    Session.printSessionList()
    
    print("Done.")
#END __main__
