import json
import urllib

from common.base import Base
from common import exceptions

class Welcome(Base):
  """ Welcome API talks to the ChatBot service.
  Inputs from the ChatBot are decoded, parsed and verified.

  Welcome message is formatted from the "name" as sent by the 
  lessenger UI, sent back to the ChatBot service,
  which then sends it back to the lessenger UI.
  """

  def __init__(self):
    Base.__init__(self)

  def ProcessClientRequest(self, environ):
    """ This method processes the HTTP request received
          from the ChatBot service.
  
      Inputs:
        environ, A WSGI environ variable.
      Outputs: 
        A welcome message.
      Raises: 
        BadQueryException, in case the user inputs are not proper.  
     """

    # Get the HTML from data received from ChatBot service.
    form_data = self.GetFormData(environ, "/Welcome")
    name = form_data.get("name")

    # Raise a BadQueryException, if "name" parameter is not
    # received from the ChatBot service. 
    if not name:
      raise exceptions.BadQueryException("'name' parameter is not available in the welcome request.")

    return name

  def __call__(self, environ, start_response):
    """ A callable method called from the welcome.wsgi application.

    Inputs:
      environ, A WSGI environ variable.
      start_response, A method to send the response back to the ChatBot service.

    Outputs:
      A welcome message back to the ChatBot service.

    Raises: 
      BadQueryException, InvalidJSONFromAPIException depending on the exception being handled.
    """

    response = ""
    try:
      status = "200 OK"

      # Retrieve user input from POST request.
      output = self.ProcessClientRequest(environ)
   
      # Format a welcome message and send it back to the ChatBot service.
      output = "Hello, %s!" %(output)
    except exceptions.InvalidJSONFromAPIException as e:
      # Handled when the inputs received from ChatBot is not as per
      # the format required by Welcome API.
      status = "204 No Content"
      output = e.message
    except exceptions.BadQueryException as e:
      # Handled when inputs from ChatBot are not valid.
      status = "400 Bad Request"
      output = e.message

    response = {
                 "message": output
               }

    # Format the response to be sent back to the ChatBot service.
    json_rsp_local = urllib.urlencode({"json": json.dumps(response)})
  
    # Sending the response back as "application/json" type.
    headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", "%s" %(str(len(json_rsp_local))))
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
