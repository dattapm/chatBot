from base import Base
from string import Template

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

    # Based on the action type, call the apropriate API
    if input_dict.get("action")[0] == "join":
       # Call the /Welcome API
       input_data = {
                      'name' : "%s" %(input_dict["name"][0]),
                      'action' : "%s" %(input_dict["action"][0]),
                      'user_id' : "%s" %(input_dict["user_id"][0])
                   }
       response = self.GetHTTPResponse(input_data, "/Welcome")
       rsp_from_api = response["message"]

       return rsp_from_api

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
       response = self.GetHTTPResponse(input_data, "/Weather")
       rsp_from_api = response["message"]

       return rsp_from_api

  def __call__(self, environ, start_response):
    status = '200 OK'

    # Retrieve user input from POST request.
    output = self.ProcessClientRequest(environ)
    
    rsp_msg_local = self.rsp_msg_template.substitute(TYPE="text",
                                                     FORMAT="text",
                                                     OUTPUT_MESSAGE=output.encode('utf-8'))

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


