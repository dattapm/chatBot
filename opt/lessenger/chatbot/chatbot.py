from string import Template

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


  def __call__(self, environ, start_response):
     status = '200 OK'
     output = 'Hello World!'

     response_headers = [
           ('Access-Control-Allow-Origin', '*'),
           ('Access-Control-Allow-Headers', 'Content-Type'),
           ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
           ('Content-Type', 'text/plain'),
         ]

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


