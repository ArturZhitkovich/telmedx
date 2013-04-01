tel*X Server code
-----------------

Notes:
- change mysite/settings.py for development: 
enable DEBUG and TEMPLATE_DEBUG. These should be set to FALSE before pushing to live server
change TEMPLATE_DIRS back to the server directory
change DATABASES:NAME to server db path


Creating the database for the first time
----------------------------------------
If you have a new copy of the repo, you will need to create the working database.
At a minimum you need to have the admin user defined. It is necessary for testing that 
we define the user as 'developer' and password is 'rootroot'. This is embedded in our unit test script.
Note that this user is NOT defined on a live production server and is only for development use.

The database will be created in the developer home directory /home/developer/db/sqlite.db
You must create have the directory /home/developer/db
 
Here is what you need to do:
developer@telX-Developer:~/workspace/telvetx$ python manage.py syncdb
ttux init: enter
ttux init: exit
Creating tables ...
Creating table auth_permission
Creating table auth_group_permissions
Creating table auth_group
Creating table auth_user_user_permissions
Creating table auth_user_groups
Creating table auth_user
Creating table django_content_type
Creating table django_session
Creating table django_site
Creating table ttux_mobilecam
Creating table ttux_sessionrecord
Creating table django_admin_log

You just installed Django's auth system, which means you don't have any superusers defined.
Would you like to create one now? (yes/no): yes
Username (leave blank to use 'developer'): 
E-mail address: 
Error: That e-mail address is invalid.
E-mail address: nobody@nowhere.com
Password: 
Password (again): 
Superuser created successfully.
Installing custom SQL ...
Installing indexes ...
Installed 0 object(s) from 0 fixture(s)
developer@telX-Developer:~/workspace/telvetx$ 




Release Notes
-------------
April 1 2013 tscott
Tag:
- added session Ticket management
- added unit tests
- first iteration of device protocol implementation (see developmentTODO.txt)

Feb 23 2013 tscott
- demo server, support multiple users and devices
- baseline github commit

March 1 2013
Tag: rel001_demo
- Tagged working demo code before cleanup

