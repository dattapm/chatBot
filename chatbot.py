from string import Template
import urllib2
import json
import cgi
from cStringIO import StringIO
#from cgi import parse_qs, escape

class ChatBot(object):

  def __init__(self):
    print "CHATBOT IS ENABLED"

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
    if content_type:
      content_type_value, content_type_dict = cgi.parse_header(content_type)
      if content_type_value == 'multipart/form-data':
        fp = environ['wsgi.input']
        user_input_dict = cgi.parse_multipart(environ['wsgi.input'], content_type_dict)

    return user_input_dict

  def ProcessClientRequest(self, environ):

    user_input_dict = self.GetFormData(environ)

    print user_input_dict.get("action")
    # Based on the action type, call the apropriate API
    if user_input_dict.get("action")[0] == "join":
       # Call the /Welcome API
       print "IN WELCOME API"
    elif user_input_dict.get("action")[0] == "message":
       print "IN MESSAGE API"

  def __call__(self, environ, start_response):
     status = '200 OK'
     output = 'Hello World!'

     response_headers = [
           ('Access-Control-Allow-Origin', '*'),
           ('Access-Control-Allow-Headers', 'Content-Type'),
           ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
           ('Content-Type', 'text/plain'),
         ]



     # Retrieve user input from POST request.
     output_new = self.ProcessClientRequest(environ)

     rsp_msg_local = self.rsp_msg_template.substitute(TYPE="text",
                                             FORMAT="text",
                                             OUTPUT_MESSAGE=output)

     json_rsp_local = self.json_response_template.substitute(MESSAGES_ARRAY=rsp_msg_local)

     response_headers.append(('Content-Length',str(len(json_rsp_local))))

     start_response(status, response_headers)

     return [json_rsp_local]

  def __del__(self):
    print "CHATBOT IS DISABLED"

def main():
  application = ChatBot() 
  application()

if __name__ == "__main__":
  main()


