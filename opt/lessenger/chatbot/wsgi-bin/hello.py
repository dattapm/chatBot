class ChatBot(object):

  def __init__(self):
    print "in init"

  def __call__(self, environ, start_response):
     status = '200 OK'
     output = 'Hello World!'

     response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]

     start_response(status, response_headers)

     return [output]

  def __del__(self):
    print "in del"

#application = ChatBot()


def main():
  application()

if __name__ == "__main__":
  application()


