import urllib2
import urllib
import json
import cgi

from common.base import Base
from string import Template
from common import exceptions

class Weather(Base):

  def __init__(self):
    self.geocoding_api_url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s"
    self.geocoding_api_key = "AIzaSyD7W7v5psM8TDJwUV2WxsPkoYRtByh07Y0"

    self.datasky_api_url = "https://api.darksky.net/forecast/%s/%s,%s"
    self.datasky_api_key = "8b4d5ca925446f9db4f7d7d0aac8b40c"

  def ProcessClientRequest(self, environ):
    form_data = self.GetFormData(environ, "/Weather")
    location = form_data.get("location")
    
    if not location:
     raise exceptions.BadQueryException("'location' parameter not available in the weather request.")

    # Call the Google Geocoding API.
    quoted_query = urllib.quote(location.lower())
    url = self.geocoding_api_url %(quoted_query, self.geocoding_api_key)

    response = self.GetExternalAPIResponse(url)

    if len(response.get("results")) == 0:
      raise exceptions.ExternalAPIException("No results returned from Google Geocoding API for query '%s'." %(quoted_query))

    if response.get("status") != "OK":
      raise exceptions.ExternalAPIException("Error '%s' received from Google Geocoding API." % response.get("error_message"))


    print "DATTA: RSP FROM WEATHER 2",response.get("status")

    # Retrieve the coordinates from the response.
    try:
      formatted_address = response["results"][0]["formatted_address"]
      latitude = response["results"][0]["geometry"]["location"]["lat"]
      longitude = response["results"][0]["geometry"]["location"]["lng"]
    except Exception as e:
      raise exceptions.InvalidJSONFromAPIException("Invalid JSON received from Google Geocoder API.")

    if not latitude or not longitude:
      raise exceptions.InvalidJSONFromAPIException("latitude or longitude not received from Google Geocoder API for user query '%s'." %(quoted_query))

    # Get the weather from Datasky API.
    url = self.datasky_api_url %(self.datasky_api_key, latitude, longitude)
    response = self.GetExternalAPIResponse(url)
    print "DATTA: RSP FROM WEATHER DATASKY:",url,latitude, longitude

    try:
      temperature = response["currently"]["temperature"]
      summary = response["currently"]["summary"]
    except Exception as e:
      raise exceptions.InvalidJSONFromAPIException("Invalid JSON received from Datasky API.")

    if not temperature or not summary:
      raise exceptions.InvalidJSONFromAPIException("forecast information not received from Datasky API.")

    forecast = "Currently it's %s F, %s." % (temperature, summary)

    return forecast

  def __call__(self, environ, start_response):
    try:
      status = "200 OK"

      # Retrieve user input from POST request.
      output = self.ProcessClientRequest(environ)
    except exceptions.InvalidJSONFromAPIException as e:
      status = "204 No Content"
      output = e.message
    except exceptions.BadQueryException as e:
      status = "400 Bad Request"
      output = e.message
    except exceptions.ExternalAPIException as e:
      print "DATTA WEATHER API EXCEPTION"
      status = "500 Internal Server Error"
      output = e.message

    rsp_format = {
                   "message" : output
                 }

    json_rsp_local = urllib.urlencode({"json": json.dumps(rsp_format)})
    headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", "%s" %(str(len(json_rsp_local))))
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


