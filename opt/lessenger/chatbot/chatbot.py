from string import Template
import urllib2
import urllib
import json
import cgi

class ChatBot(object):

  def __init__(self):
    print "CHATBOT IS ENABLED"

    self.SERVER_URL = "http://localhost:9000"
    self.HEADERS = [
           ('Access-Control-Allow-Origin', '*'),
           ('Access-Control-Allow-Headers', 'Content-Type'),
           ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
           ('Content-Type', 'text/plain'),
         ]

    self.json_response = """
        {
             "messages": [
                 ${MESSAGES_ARRAY}
             ]
        }\
       """

    self.rsp_msg = """
        {
              "type": "${TYPE}",
              "${FORMAT}": "${OUTPUT_MESSAGE}"
        }\
       """

    self.json_response_template = Template(self.json_response)
    self.rsp_msg_template = Template(self.rsp_msg)


  def GetFormData(self, environ):
    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.

    content_type = environ['CONTENT_TYPE']
    user_input_dict = {}
    if content_type:
      content_type_value, content_type_dict = cgi.parse_header(content_type)
      if content_type_value == 'multipart/form-data':
        user_input_dict = cgi.parse_multipart(environ['wsgi.input'], content_type_dict)
      elif content_type_value == 'application/json':
        try:
          request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
          request_body_size = 0

        # When the method is POST the variable will be sent
        # in the HTTP request body which is passed by the WSGI server
        # in the file like wsgi.input environment variable.
        request_body = environ['wsgi.input'].read(request_body_size)
        request_body = cgi.parse_qs(request_body)
        user_input_dict = json.loads(request_body["json"][0])


    return user_input_dict

  def ProcessClientRequest(self, environ):

    input_dict = self.GetFormData(environ)

    # Based on the action type, call the apropriate API
    if input_dict.get("action")[0] == "join":
       # Call the /Welcome API
       input_data = {
                      'name' : "%s" %(input_dict["name"][0]),
                      'action' : "%s" %(input_dict["action"][0]),
                      'user_id' : "%s" %(input_dict["user_id"][0])
                   }

       data = urllib.urlencode({"json": json.dumps(input_data)})

       url = self.SERVER_URL + "/Welcome"
       headers = {
                   'Content-Type': 'application/json'
                 }
       req = urllib2.Request(url, data, headers)
       response = urllib2.urlopen(req)
       rsp_from_welcome_api = json.loads(cgi.parse_qs(response.read())["json"][0])["message"]

       return rsp_from_welcome_api

    elif input_dict.get("action")[0] == "message":
       # Extract the city information from the query.
       import re

       print "IN MESSAGE API"
       user_location = input_dict["text"][0]

       """ 
       weather in <Location>
       <Location> weather
       """

       match = re.search(r'what\'s\s+the\s+weather\s+in\s+([a-zA-Z0-9 ]*.*)',user_location, re.IGNORECASE)

       print "DATTA: MSG API 1", match
       if match:
         matches = match.groups()
         
         # pick up the first one in case of multiple inputs
         location = matches[0] 
       else:
         print "USER DIDN'T PROVIDE ANY VALID INPUT"

       print "DATTA: MSG API 2", matches, location
       input_data = {
                      'location' : "%s" %(location),
                      'action' : "%s" %(input_dict["action"][0]),
                      'user_id' : "%s" %(input_dict["user_id"][0])
                    }
       print "DATTA: MSG API 3", input_data
       data = urllib.urlencode({"json": json.dumps(input_data)})

       url = self.SERVER_URL + "/Weather"
       headers = {
                   'Content-Type': 'application/json'
                 }
       req = urllib2.Request(url, data, headers)
       response = urllib2.urlopen(req)
       rsp_from_weather_api = json.loads(cgi.parse_qs(response.read())["json"][0])["message"]

       return rsp_from_weather_api

  def __call__(self, environ, start_response):
     status = '200 OK'

     # Retrieve user input from POST request.
     output = self.ProcessClientRequest(environ)
    
     rsp_msg_local = self.rsp_msg_template.substitute(TYPE="text",
                                                      FORMAT="text",
                                                      OUTPUT_MESSAGE=output.encode('utf-8'))
     json_rsp_local = self.json_response_template.substitute(MESSAGES_ARRAY=rsp_msg_local)
     self.HEADERS.append(('Content-Length',str(len(json_rsp_local))))
     start_response(status, self.HEADERS)

     return [json_rsp_local]

  def __del__(self):
    print "CHATBOT IS DISABLED"

def main():
  application = ChatBot() 
  application()

if __name__ == "__main__":
  main()


