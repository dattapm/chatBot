import json
import urllib

from common.base import Base
from common import exceptions

class Welcome(Base):
  def __init__(self):
    pass

  def ProcessClientRequest(self, environ):
    form_data = self.GetFormData(environ, "/Welcome")
    name = form_data.get("name")

    if not name:
      raise exceptions.BadQueryException("'name' parameter not available in the welcome request.")

    return name

  def __call__(self, environ, start_response):
    response = ""
    try:
      status = "200 OK"
      # Retrieve user input from POST request.
      output = self.ProcessClientRequest(environ)
      output = "Hello, %s!" %(output)
    except exceptions.InvalidJSONFromAPIException as e:
      status = "204 No Content"
      output = e.message
    except exceptions.BadQueryException as e:
      status = "400 Bad Request"
      output = e.message

    response = {
                 "message": output
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
