from string import Template
import urllib2
import urllib
import json
import cgi

class Welcome(object):

  def __init__(self):
    print "IN WELCOME API"

    self.SERVER_URL = "http://localhost:9000/Welcome"
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


    form_data = {}

    content_type = environ['CONTENT_TYPE']
    if content_type:
      content_type_value, content_type_dict = cgi.parse_header(content_type)
      if content_type_value == 'multipart/form-data':
        form_data = cgi.parse_multipart(environ['wsgi.input'], content_type_dict)
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
        form_data = json.loads(request_body["json"][0])
  
    return form_data

  def ProcessClientRequest(self, environ):
    form_data = self.GetFormData(environ)

    return form_data["name"]

  def __call__(self, environ, start_response):
     status = '200 OK'

     # Retrieve user input from POST request.
     output = self.ProcessClientRequest(environ)

     output = "Hello, %s! " %(output)

     rsp_format = {
                    "message" : output
                  }

     json_rsp_local = urllib.urlencode({"json": json.dumps(rsp_format)})

     headers = [
                 ('Content-Type', 'application/json'),
                 ('Content-Length', '%s' %(str(len(json_rsp_local))))
               ]

     start_response(status, headers)

     return [json_rsp_local]

  def __del__(self):
    print "CHATBOT IS DISABLED"

def main():
  application = Welcome() 
  application()

if __name__ == "__main__":
  main()


