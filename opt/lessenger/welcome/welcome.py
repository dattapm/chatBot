import json
import urllib

from common.base import Base
from common import exceptions

class Welcome(Base):

  def __init__(self):
    pass

  def ProcessClientRequest(self, environ):
    form_data = self.GetFormData(environ)

    return form_data["name"]

  def __call__(self, environ, start_response):

    try:
      status = "200 OK"
      # Retrieve user input from POST request.
      output = self.ProcessClientRequest(environ)
      output = "Hello, %s!" %(output)
      response = {
                   "message" : output
                 }
    except exceptions.InvalidJSONResponseException as e:
      print "WELCOME API: JSON EXP"
      status = "400 Bad Request"
      response = {
                   "message" : e
                 }

    json_rsp_local = urllib.urlencode({"json": json.dumps(response)})
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


