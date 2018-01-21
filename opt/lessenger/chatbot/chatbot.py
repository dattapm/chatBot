import re

from common.base import Base
from string import Template
from common import exceptions

class ChatBot(Base):

  def __init__(self):
    Base.__init__(self)

    self.ui_headers = [
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

  def ProcessClientRequest(self, environ):

    input_dict = self.GetFormData(environ)
    if input_dict:
      if input_dict.get("action"): 
        # Based on the action type, call the appropriate API.
        if input_dict.get("action")[0] == "join":
           # Call the "/Welcome" API.

           name =  input_dict.get("name")[0] if input_dict.get("name") else None
           action = input_dict.get("action")[0] if input_dict.get("action") else None
           user_id = input_dict.get("user_id")[0] if input_dict.get("user_id") else None

           if not name or not action or not user_id:
	     raise exceptions.BadQueryException("'join' action item should have 'name', 'action' and 'user_id' information.")

           input_data = {
                          "name" : name,
                          "action" : action,
                          "user_id" : user_id
                        }

           response = self.GetHTTPResponse(input_data, "/Welcome")
           rsp_from_api = response["message"]

           return rsp_from_api

        elif input_dict.get("action")[0] == "message":
           # Extract the city information from the query.

           text = input_dict.get("text")[0] if input_dict.get("text") else None
           action = input_dict.get("action")[0] if input_dict.get("action") else None
           user_id = input_dict.get("user_id")[0] if input_dict.get("user_id") else None

           if not text or not action or not user_id:
	     raise exceptions.BadQueryException("'message' action item should have 'text', 'action' and 'user_id' information.")

           """ 
           weather in <Location>
           <Location> weather
           """ 

           match = re.search(r'what\'s\s+the\s+weather\s+in\s+([a-zA-Z0-9 ]*.*)', text, re.IGNORECASE)

           if match:
             matches = match.groups()
             # pick up the first one in case of multiple inputs
             location = matches[0] 
  
           if not match or not location:
	     raise exceptions.BadQueryException("Please enter valid city /country name of zip code.")

           # Check if location is valid here.
           input_data = {
                          "location" : location,
                          "action" : action,
                          "user_id" : user_id
                        }

           response = self.GetHTTPResponse(input_data, "/Weather")
           rsp_from_api = response["message"]

           return rsp_from_api
        else:
          raise exceptions.BadQueryException("'action' should be either 'join' or 'message'.")
      else:
        raise exceptions.BadQueryException("Valid 'action' not received from lessenger UI.")
    else:
      raise exceptions.BadQueryException("Valid input's not received from lessenger UI.")

  def __call__(self, environ, start_response):

    try:
      # Retrieve user input from POST request.
      status = '200 OK'
      output = self.ProcessClientRequest(environ)
      rsp_msg_local = self.rsp_msg_template.substitute(
        TYPE="text", FORMAT="text", OUTPUT_MESSAGE=output.encode('utf-8'))
    except exceptions.BadQueryException as e:
      status = "400 Bad Request"
      rsp_msg_local = self.rsp_msg_template.substitute(
        TYPE="text", FORMAT="text", OUTPUT_MESSAGE="ChatBot: %s" %e)
      print "IN BAD QUERY EXCEPTION"
    except exceptions.HTTPRequestException as e:
      status = "400 Bad Request"
      rsp_msg_local = self.rsp_msg_template.substitute(
        TYPE="text", FORMAT="text", OUTPUT_MESSAGE="ChatBot: %s" %e)
    except exceptions.UnsupportedMediaTypeException as e:
      status = "415 Unsupported Media Type"
      rsp_msg_local = self.rsp_msg_template.substitute(
        TYPE="text", FORMAT="text", OUTPUT_MESSAGE="ChatBot: %s" %e)
      
    json_rsp_local = self.json_response_template.substitute(MESSAGES_ARRAY=rsp_msg_local)
    self.ui_headers.append(('Content-Length',str(len(json_rsp_local))))
    start_response(status, self.ui_headers)
    return [json_rsp_local]

  def __del__(self):
    pass

def main():
  application = ChatBot() 
  application()

if __name__ == "__main__":
  main()


