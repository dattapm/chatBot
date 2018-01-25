
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
5. Add "/opt/lessenger/conf/lessenger.conf" to the httpd.conf, as a 'conf' fle which needs to be run by the 
   Apache server.
6. The above lessenger.conf file contains settings to listen to port 9000 and process the HTTP requests arriving at 
   this port.
7. Restart the web server.
8. If all the permissions look good, then the lessenger UI should be able to contact the backend WSGI applications. 
9. Try to enter a name and expect the server to respond back with a "Hello, \<name\>"
10. Then enter location details to get the forecast information.

Insight into the backend design:
---------------------------------
Backend has been designed to have a service 'ChatBot' running at port 9000 and two APIs, namely 'Welcome' and 'Weather', which run at '/Welcome' and '/Weather' respectively.

'ChatBot' interacts with the two APIs over HTTP with JSON as the message format. More details of the message format have been provided in the same document.

'/Welcome' API takes a name and returns a welcome message to be displayed on the lessenger UI.

'/Weather' API takes a location parameter and internally calls two public APIs(Google Geocoding and Datasky APIs) to get the latitude/ longitude and weather forecast respectively.

Advantages of having 'Welcome' and 'Weather' as two APIs:
---------------------------------------------------------
The functionality of sending the welcome message and weather forecast could have been in-built along with the ChatBot service, but there are advantages of running them as APIs, as mentioned below:

1. The two APIs could be hosted on different servers as required by the system requirements. Since the ChatBot service
   interacts with the APIs over HTTP, they could be communicated across the network.
2. The technology stack of the APIs could be different, as demanded by the project requirements. Since the message
   exchange is happening over HTTP with JSON, it is enough that the message exchange happens in JSON.
3. The two APIs could be managed, maintained and evolved by different people, thus making it developer-independent.  



Block Diagram of the entities running in the backend:                 
-----------------------------------------------------    

![alt text](https://raw.githubusercontent.com/dattapm/lessenger/master/opt/lessenger/common/lessenger_diagram.png)

JSON format exchanged between ChatBot and Welcome/ Weather APIs:
---------------------------------------------------------------

The JSON format being exchanged from ChatBot service to Welcome API is as below:

   {

         "json" : {
  
                      "name" : name,
              
                      "action" : action,
              
                      "user_id" : user_id
              
                   }
           
   }

The JSON format being exchanged from Welcome API to ChatBot service is as below:

   {

         "json" : {
   
                      "message" : output
               
                  }
            
   }

The JSON format being exchanged from ChatBot service to Weather API is as below:

   {

         "json": {
   
                      "location" : location,
               
                      "action" : action,
               
                      "user_id" : user_id
               
                 }
           
    }
 
 The JSON format being exchanged from Weather API to ChatBot service is as below:
 
    {
 
         "json" : {
   
                       "message" : output
               
                  }
            
    }

Here, "output" is the text that is displayed on the lessenger UI.
 
Error/ Exception handling:
--------------------------

Depending on the requirement, the below exceptions have been customized to reflect the type of issue handled.
```
1. BadQueryException: 

      Raised when the inputs received by the API are not as per the requirements.
     
2. HTTPRequestException:

     Raised when proper inputs are not received in the HTTP request.
     
3. UnsupportedMediaTypeException:

     Raised when the Content-Type received in the HTTP request is not supported by the backend.
     
4. ServerNotAvailableException:

     Raised when the server hosting the ChatBot service or private APIs(Welcome and Weather) or public APIs
     (Google Geocoding and Datasky APIs) are not reachable.
     
5. validJSONFromAPIException:

     Raised when the JSON request/ response is not as per the format expected.
     
6. ExternalAPIException:

     Raised when the information exchange between the Weather API and the public APIs(Google Geocoding and Datasky APIs)
     are not as expected.
     
7. UnknownException:

     Raised for any other exception not handled in the above scenarios.
```

Technology stack used:                                                                      
----------------------
The software in this repository has been tested for the below environment.

1. Python version is 2.x(2.7.5)
2. Ubuntu 16.04.2 LTS.
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
