import urllib2
import urllib
import json
import cgi

from common.base import Base
from string import Template

class Weather(Base):

  def __init__(self):
    self.geocoding_api_url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s"
    self.geocoding_api_key = "AIzaSyD7W7v5psM8TDJwUV2WxsPkoYRtByh07Y0"

    self.datasky_api_url = "https://api.darksky.net/forecast/%s/%s,%s"
    self.datasky_api_key = "8b4d5ca925446f9db4f7d7d0aac8b40c"

  def ProcessClientRequest(self, environ):
    form_data = self.GetFormData(environ, "/Weather")

    # Call the Google Geocoding API.

    location = form_data["location"]

    quoted_query = urllib.quote(location.lower())
    url = self.geocoding_api_url %(quoted_query, self.geocoding_api_key)

    response = urllib2.urlopen(url)
    rsp_from_google_api = json.loads(response.read())

    # Retrieve the coordinates from the response.
    formatted_address = rsp_from_google_api["results"][0]["formatted_address"]
    latitude = rsp_from_google_api["results"][0]["geometry"]["location"]["lat"]
    longitude = rsp_from_google_api["results"][0]["geometry"]["location"]["lng"]
    
    # Get the weather from Datasky API.
    url = self.datasky_api_url %(self.datasky_api_key, latitude, longitude)

    response = urllib2.urlopen(url)
    rsp_from_datasky_api = json.loads(response.read())

    temperature = rsp_from_datasky_api["currently"]["temperature"]
    summary = rsp_from_datasky_api["currently"]["summary"]

    forecast = "Currently it's %s F, %s." % (temperature, summary)

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
    pass

def main():
  application = Weather() 
  application()

if __name__ == "__main__":
  main()


