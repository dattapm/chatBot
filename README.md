
Introduction:
-------------

This repository contains the entire backend code for running a chatbot engine which can interact with the lessenger UI. User enters the 'name' and then a 'location' parameter in the frontend UI. The UI sends this information back to the backend, which uses this data to greet the person and then provide a forecast of the weather at the 'location'. The 'location' can be entered in three different patterns as described in the API specs. The user has also the flexibility to enter a city or country or zip code as the 'location' parameter. 

lessenger API specs:
--------------------
Pattern of the inputs and the expected outputs have been documented below:

https://github.com/Hipmunk/hipproblems/blob/master/lessenger/api.md

The URL to access the lessenger UI is available in the below link:

https://github.com/Hipmunk/hipproblems/blob/master/lessenger/README.md

Technical requirements to run the backend server:
-------------------------------------------------

1. Install Apache web server and configure it to run at port 9000 on the localhost.
2. Install mod_wsgi and configure it to use the web server above.
3. Download the github repository. This should copy all the folders/ files into the path "/opt/lessenger/ locally.
4. Make sure you have the required permissions to execute the python modules(usually a 755 will do).
5. Add "/opt/lessenger/conf/lessenger.conf" to the httpd.conf, as a 'conf' fle which needs to be run by the Apache 
server.
6. The above lessenger.conf file contains settings to listen to port 9000 and process the HTTP requests arriving at this port.
7. Restart the web server.
8. If all the permissions look good, then the lessenger UI should be able to contact the backend WSGI applications. 
9. Try to enter a name and expect the server to respond back with a "Hello, <name>"
10. Then enter location details to get the forecast information.

Technology stack used:
----------------------

The software in this repository has been tested for the following requirements.

1. Python version is 2.x(2.7.5)
2. This code has been tested for proper functioning on Ubuntu 16.04.2 LTS.
3. The frontend has been tested for proper functioning on Chrome and FireFox browsers.

Isssues found with the lessenger UI:
-----------------------------------
1. Error 204 (NO CONTENT) was not being handled properly by the lessener UI. UI reports a generic message rather than the
   one sent from the backend server.
2. There is a provision to send the response back to the UI in html format(as type 'rich'). But this format has no impact 
   on the UI. UI still displays the html message as normal text.

Some further improvement's that can be made are as follows:
-----------------------------------------------------------
1. Add support for logging module, which wil help in logging to a file at /opt/lessenger,
   which help us in easy debugging and troubleshooting of the issues.
2. Support unicode in user text entries.
3. Add support for user_id checking to make sure that the forecast information that we are sending to is the one who
   has asked for it.
