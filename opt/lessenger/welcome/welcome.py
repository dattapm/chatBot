import json
import urllib
import logging
import logging.config

from common.base import Base
from common import exceptions

class Welcome(Base):
  def __init__(self):
    Base.__init__(self)
    #logging.config.fileConfig("/opt/lessenger/conf/logging.conf", disable_existing_loggers=False)
    #self.logger = logging.getLogger("lessenger_ui")

  def ProcessClientRequest(self, environ):
    form_data = self.GetFormData(environ, "/Welcome")
    name = form_data.get("name")

    #self.logger.info("WELCOME API 1: Parameter name received is %s",name)
    if not name:
      msg = "'name' parameter is not available in the welcome request."
      #self.logger.error("WELCOME API: %s",msg)
      raise exceptions.BadQueryException(msg)

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
