'''
Created on 2013-03-31

@author: developer
'''
# RETURN CODES
RC_BAD_SUID         = "BAD_SUID"
RC_REGISTER_OK      = "REGISTER_OK"
RC_REGISTER_FAIL    = "REGISTER_FAIL"

RC_SESSION_OK       = "SESSION_OK"
RC_SESSION_FAIL     = "SESSION_FAIL"

# HTTP STATUS CODES
HSTAT_OK            = 200
HSTAT_AUTH_FAIL     = 418
#HSTAT_BAD_DEVICE    = 418   # HTTP status code returned when the device SUID does not exist in the REGISTRY
HSTAT_LOGIN_SUCCESS = 302   # HTTP status coder returned after successful login to django
HSTAT_NO_KEYS_LEFT  = 418   # server ran out of Tickets
HSTAT_BAD_REQUEST   = 400   # returned for an incorrectly formatted request
HSTAT_NOT_FOUND     = 404   # returned by django for an invalid url