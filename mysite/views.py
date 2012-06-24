from django.http import HttpResponse
from flashpolicies import policies

# adobe flash crossdomain.xml handler
def crossdomainHandler(request):
#    print("handling crossdomain.xml request")
#    responseStr="<cross-domain-policy> <allow-access-from domain='*' to-ports='*' /> </cross-domain-policy>"
#    resp = HttpResponse( responseStr, mimetype="text/xml") 
#    return resp

    my_policy = policies.Policy();
    my_policy.allow_domain("*", to_ports="*");
    print "returning policy response: \n" + str(my_policy)
    response =  HttpResponse( str(my_policy) )
    response['Content-Type'] ='text/x-cross-domain-policy'
    return response
