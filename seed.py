import os

def populate():
	g = add_group('Users')

	add_cam( g=g, name='Brian_Phone', uid='12345678910')
	add_cam( g=g, name='Brad_Phone', uid='12345678910')

	g.user_set.add(User.objects.all()[0])

def add_cam(g, name, uid):
    c = mobileCam.objects.get_or_create( groups=g, name=name, uid=uid)[0]
    return c

def add_group(name):
    g = Group.objects.get_or_create(name=name)[0]
    return g

# Start execution here!
if __name__ == '__main__':
    print "Starting ttux population script..."
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    from ttux.models import mobileCam
    from django.contrib.auth.models import Group, User
    populate()