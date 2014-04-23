import os

full = ["BradsPhone", "RicksPhone", "demoTouch1", "ZbyszeksPhone", "JohnR_iTouch", "Brad_iPad2", "Max_iPhone", "JohnR_iPad3", "Rick_iPad3", "Phil_iTouch", "Max_iPad", "Brad_GalaxyS3", "Zbyszek_Xperia", "JohnR_GalaxyS4", "DavidK_GalaxyS3", "RobertO_GalaxyTab", "RobertO_Stratosphere", "Bob_Schack", "RobertO_GalaxyS3", "Carney1", "MikeBGalaxyS3", "fitz1", "Gerard", "TMeier", "JohnG_iPhone5", "Jeanne", "JTipler", "CTipler", "KTipler", "JohnRoss1", "JohnRoss2", "JohnRoss3", "WillyOrtiz", "GaryRotto", "GregSchnitzerS4", "BrianAnglin", "telmedxSpanish"];

def populate():
	g = add_group('Users')

	# add_cam( g=g, name='Brian_Phone', uid='12345678910')
	# add_cam( g=g, name='Brad_Phone', uid='12345678910')
	for name in full:
		add_cam( g=g, name=name, uid='12345678910')
		
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