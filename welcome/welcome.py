import cgi
import json
import urllib
import urllib2

from string import Template
from chatbot.base import Base

class Welcome(Base):

  def __init__(self):
    pass

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
    pass

def main():
  application = Welcome() 
  application()

if __name__ == "__main__":
  main()


