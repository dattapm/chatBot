import re

from common.base import Base
from string import Template
from common import exceptions

class ChatBot(Base):
  """ ChatBot interacts with the lessenger UI.
      
      Any inputs from the UI are handled in this class and
      the responses are sent from here.

      ChatBot interacts with the /Welcome and /Weather APIs.
      All the responses from the APIs(proper output, errors or exceptions
      are processed and sent back to the lessenger UI.
  """

  def __init__(self):
    Base.__init__(self)

    # CORS headers added here. 
    self.ui_headers = [
           ("Access-Control-Allow-Origin", "*"),
           ("Access-Control-Allow-Headers", "Content-Type"),
           ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
           ("Content-Type", "text/plain"),
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

    # Pattern's of the three types of queries which the end user can enter
    # on the lessenger UI.

    self.location_pattern_strings = [
        r"\s*what\'s\s+the\s+weather\s+in\s+([a-zA-Z0-9 ]*.*)\s*",
        r"\s*weather\s+in\s+([a-zA-Z0-9 ]*.*)\s*",
        r"\s*([a-zA-Z0-9 ]*.*)weather\s*"
        ]

  def ProcessClientRequest(self, environ):
    """ This method processes the HTTP request received
        from the lessenger UI.

        It also processes the HTTP requests sent from the
        ChatBot service to the 'Welcome' and 'Weather' APIs.

    Inputs:
      environ, A WSGI environ variable.
    Outputs: 
      A welcome message or a forecast, depending on the 'action' key.
    Raises: 
      BadQueryException, in case the user inputs are not proper.  
    """          

    # Fetch the HTTP form data to get the user entered data.
    input_dict = self.GetFormData(environ)
    api_name = ""
    if input_dict:
      if input_dict.get("action"): 
        # Based on the action type, call the appropriate API.
        if input_dict.get("action")[0] == "join":
          # Action type is "join" when the user 
          # enters a name in the name box.
          # Call the "/Welcome" API to fetch the welcome message.

          api_name = "/Welcome"
          name =  input_dict.get("name")[0] if input_dict.get("name") else None
          action = input_dict.get("action")[0] if input_dict.get("action") else None
          user_id = input_dict.get("user_id")[0] if input_dict.get("user_id") else None


          # if there is no 'name' or 'action' or 'user_id' details in the HTTP form,
          # then send a BadQueryException back to the lessenger UI. 
          if not name or not action or not user_id:
	    raise exceptions.BadQueryException("'join' action item should have 'name', 'action' and 'user_id' information.")

          input_data = {
                         "name" : name,
                         "action" : action,
                         "user_id" : user_id
                       }
        elif input_dict.get("action")[0] == "message":
          # Action type is "message" when the user 
          # enters a query to get the forecast.

          # Call the "/Weather" API to fetch the forecast.

          # Extract the location information from the query.
          api_name = "/Weather"
          text = input_dict.get("text")[0] if input_dict.get("text") else None
          action = input_dict.get("action")[0] if input_dict.get("action") else None
          user_id = input_dict.get("user_id")[0] if input_dict.get("user_id") else None


          # if there is no "text" or "action" or "user_id" details in the HTTP form,
          # then send a BadQueryException back to the lessenger UI. 
          if not text or not action or not user_id:
	    raise exceptions.BadQueryException("'message' action item should have 'text', 'action' and 'user_id' information.")

          # The below check for the three different formats of user inputs could have been 
          # handled as a single check, but for some reason, it doesn't work as expected.

          # Presently trying to check for a match by querying each pattern seperately.

          match = re.search(self.location_pattern_strings[0], text, re.IGNORECASE)
          if match:
            matches = match.groups()
            # pick up the first one in case of multiple inputs
            location = matches[0] 
          else:
            match = re.search(self.location_pattern_strings[1], text, re.IGNORECASE)
            if match:
              matches = match.groups()
              # pick up the first one in case of multiple inputs
              location = matches[0]
            else: 
              match = re.search(self.location_pattern_strings[2], text, re.IGNORECASE)
              if match:
                matches = match.groups()
                # pick up the first one in case of multiple inputs
                location = matches[0]
             
          # Check if location is valid here.

          # If there is no proper location information in the 
          # user query, then send a BadQueryException back to the lessenger UI.
          if not match or not location:
	    raise exceptions.BadQueryException("Please enter valid city/ country name or zip code."
                                               " "
                                               "Usage is:"
                                               " what's the weather in <Location> or"
                                               " weather in <Location> or"
                                               " <Location> weather")

          input_data = {
                          "location" : location,
                          "action" : action,
                          "user_id" : user_id
                       }
        else:
          # Raise BadQueryException if the action is not valid.
          raise exceptions.BadQueryException("'action' should be either 'join' or 'message'.")

        # Send a HTTP request to the API.
        return self.GetHTTPResponse(input_data, api_name)
      else:
        # Raise BadQueryException if there is no 'action' key from the lseenger UI.
        raise exceptions.BadQueryException("Valid 'action' not received from lessenger UI.")
    else: 
      # Raise BadQueryException if no proper inputs received from the lessenger UI.
      raise exceptions.BadQueryException("Valid input's not received from lessenger UI.")


  def __call__(self, environ, start_response):
    """ A callable method called from the chatbot.wsgi application.

    Inputs:
      environ, A WSGI environ variable.
      start_response, A method to send the response back to the lessenger UI.

    Outputs:
      A response back to the lessenger UI.

    Raises: 
      BadQueryException, HTTPRequestException, UnsupportedMediaTypeException,
      InvalidJSONFromAPIException, ServerNotAvailableException, UnknownException, depending on the
      exception being handled.
    """
         
    try:
   
      # A successful scenario when a valid input is received and 
      # handled by the ChatBot engine.  
      status = "200 OK"

      # Retrieve user input from POST request.
      output = self.ProcessClientRequest(environ)
     
      # Format the response as per the lessenger API document.
      rsp_msg_local = self.rsp_msg_template.substitute(
        TYPE="text", FORMAT="text", OUTPUT_MESSAGE=output)
    except (exceptions.BadQueryException, exceptions.HTTPRequestException) as e:
      # Handled when the inputs received by the API are not as per the requirements.
      # or when proper inputs are not received in the HTTP request.
      status = "400 Bad Request"
      rsp_msg_local = self.rsp_msg_template.substitute(
        TYPE="text", FORMAT="text", OUTPUT_MESSAGE="ChatBot: %s" % e.message)
    except exceptions.UnsupportedMediaTypeException as e:
      # Handled when the Content-Type is not what we are expecting.
      status = "415 Unsupported Media Type"
      rsp_msg_local = self.rsp_msg_template.substitute(
        TYPE="text", FORMAT="text", OUTPUT_MESSAGE="ChatBot: %s" % e.message)
    except exceptions.InvalidJSONFromAPIException as e:
      # Handled when the JSON request/ response is not as per the format.
      # Please see the design or README document for the valid formats.
      status = "204 No Content"
      rsp_msg_local = self.rsp_msg_template.substitute(
        TYPE="text", FORMAT="text", OUTPUT_MESSAGE="ChatBot: %s" % e.message)
    except (exceptions.ServerNotAvailableException, exceptions.UnknownException) as e:
      # Handled when the servers hosting the ChatBot or the APIs(internal and external)
      # are not available or when any unknown error occurs. 
      status = "500 Internal Server Error"
      rsp_msg_local = self.rsp_msg_template.substitute(
        TYPE="text", FORMAT="text", OUTPUT_MESSAGE="ChatBot: %s" % e.message)

    # Format the response as per the UI requirements.
    json_rsp_local = self.json_response_template.substitute(MESSAGES_ARRAY=rsp_msg_local).encode("utf-8")

    self.ui_headers.append(("Content-Length",str(len(json_rsp_local))))
    start_response(status, self.ui_headers)

    # Send back the response to the lessenger UI.
    return [json_rsp_local]

  def __del__(self):
    pass

def main():
  application = ChatBot() 
  application()

if __name__ == "__main__":
  main()
