from string import Template
import urllib2
import urllib
import json
import cgi

class Weather(object):

  def __init__(self):
    print "IN WEATHER API"

    self.SERVER_URL = "http://localhost:9000/Weather"
    self.HEADERS = [
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

    self.GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s"
    self.GEOCODING_API_KEY = "AIzaSyD7W7v5psM8TDJwUV2WxsPkoYRtByh07Y0"

    self.DATASKY_API_URL = "https://api.darksky.net/forecast/%s/%s,%s"
    self.DATASKY_API_KEY = "8b4d5ca925446f9db4f7d7d0aac8b40c"

  def GetFormData(self, environ):
    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.


    form_data = {}

    content_type = environ['CONTENT_TYPE']
    if content_type:
      content_type_value, content_type_dict = cgi.parse_header(content_type)
      if content_type_value == 'multipart/form-data':
        form_data = cgi.parse_multipart(environ['wsgi.input'], content_type_dict)
      elif content_type_value == 'application/json':
        try:
          request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
          request_body_size = 0

        # When the method is POST the variable will be sent
        # in the HTTP request body which is passed by the WSGI server
        # in the file like wsgi.input environment variable.
        request_body = environ['wsgi.input'].read(request_body_size)
        request_body = cgi.parse_qs(request_body)
        form_data = json.loads(request_body["json"][0])
  
    return form_data

  def ProcessClientRequest(self, environ):
    form_data = self.GetFormData(environ)

    # Call the Google Geocoding API.

    location = form_data["location"]

    quoted_query = urllib.quote(location.lower())
    url = self.GEOCODING_API_URL %(quoted_query, self.GEOCODING_API_KEY)

    response = urllib2.urlopen(url)
    rsp_from_google_api = json.loads(response.read())

    # Retrieve the coordinates from the response.
    formatted_address = rsp_from_google_api["results"][0]["formatted_address"]
    latitude = rsp_from_google_api["results"][0]["geometry"]["location"]["lat"]
    longitude = rsp_from_google_api["results"][0]["geometry"]["location"]["lng"]
    

    # Get the weather from Datasky API.
    url = self.DATASKY_API_URL %(self.DATASKY_API_KEY, latitude, longitude)

    response = urllib2.urlopen(url)
    rsp_from_datasky_api = json.loads(response.read())

    temperature = rsp_from_datasky_api["currently"]["temperature"]
    summary = rsp_from_datasky_api["currently"]["summary"]

    forecast = "Currrently it's %s F, %s." % (temperature, summary)

    return forecast

  def __call__(self, environ, start_response):
     status = '200 OK'

     # Retrieve user input from POST request.
     output = self.ProcessClientRequest(environ)

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
    print "WEATHER IS DISABLED"

def main():
  application = Weather() 
  application()

if __name__ == "__main__":
  main()


