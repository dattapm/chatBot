import urllib2
import urllib
import json
import cgi

from common.base import Base
from string import Template
from common import exceptions

class Weather(Base):
  """ Weather API talks to ChatBot service on one hand and
  Google Geocoding and Datasky APIs on the other hand.

  Inputs from the ChatBot are decoded, parsed and verified.

  If the inputs are valid, then a HTTP request is sent to the 
  Google Geocoding API to fetch the latitude and longitude of the
  location. 

  If the latitude and longitude are valid, then a HTTP request is sent
  to the Datasky API to get forecast information.
  
  Forecast information is formatted, sent back to the ChatBot service,
  which then sends it back to the lessenger UI.
  """ 
  
  def __init__(self):
    Base.__init__(self)
    # URLs and keys to talk to the Public APIs.
    self.geocoding_api_url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s"
    self.geocoding_api_key = "AIzaSyD7W7v5psM8TDJwUV2WxsPkoYRtByh07Y0"

    self.datasky_api_url = "https://api.darksky.net/forecast/%s/%s,%s"
    self.datasky_api_key = "8b4d5ca925446f9db4f7d7d0aac8b40c"

  def ProcessClientRequest(self, environ):
    """ This method processes the HTTP request received
    from the ChatBot service.

    Inputs:
      environ, A WSGI environ variable.
    Outputs: 
      A forecast message based on user inputs.
    Raises: 
      BadQueryException, ExternalAPIException,InvalidJSONFromAPIException as handled per requirement.
    """
    # Get the HTML form data received from the ChatBot service.
    form_data = self.GetFormData(environ, "/Weather")

    # Get the location information as entered by the user.
    location = form_data.get("location")
    
    # Raise BadQueryException in case "location" information is not available in the request.
    if not location:
      raise exceptions.BadQueryException("'location' parameter not available in the weather request.")

    # Call the Google Geocoding API.
    quoted_query = urllib.quote(location.lower())
    url = self.geocoding_api_url %(quoted_query, self.geocoding_api_key)

    # Get the response from the Google Geocoding API.
    response = self.GetExternalAPIResponse(url)

    # If there are no results returned from the Google Geocoding API, for a user query, then raise an error with
    # appropriate message back to the ChatBot service. 
    if len(response.get("results")) == 0:
      raise exceptions.ExternalAPIException("No results returned from Google Geocoding API for query '%s'." %(quoted_query))

    # If the response from the Google Geocoding API is not "OK", then raise a ExternalAPIException with an 
    # appropriate exception back to the ChatBot service.
    if response.get("status") != "OK":
      raise exceptions.ExternalAPIException("Error '%s' received from Google Geocoding API." % response.get("error_message"))

    # Retrieve the coordinates from the response.
    try:
      # Consider only the first result, in case of multiple results.
      formatted_address = response["results"][0]["formatted_address"]
      latitude = response["results"][0]["geometry"]["location"]["lat"]
      longitude = response["results"][0]["geometry"]["location"]["lng"]
    except Exception as e:
      # Raise an exception in case the response from the Google Geocoding API doesn't contain the required data.
      raise exceptions.InvalidJSONFromAPIException("Invalid JSON received from Google Geocoder API.")

    if not latitude or not longitude:
      # If there is no latitude or longitude information, then there is no use proceeding further.
      # Raise an exception and send it back to the ChatBot service.
      raise exceptions.InvalidJSONFromAPIException("latitude or longitude not received from Google Geocoder API for user query '%s'." %(quoted_query))

    # Get the weather from Datasky API.
    url = self.datasky_api_url %(self.datasky_api_key, latitude, longitude)

    # Get the response from the Google Geocoding API.
    response = self.GetExternalAPIResponse(url)

    try:
      temperature = response["currently"]["temperature"]
      summary = response["currently"]["summary"]
    except Exception as e:
      # If there is no temperature or summary information from Datasky API, then 
      # raise an exception back to the ChatBot service.
      raise exceptions.InvalidJSONFromAPIException("Invalid JSON received from Datasky API.")

    # If temperature or summary information from Datasky API is empty, then 
    # raise an exception back to the ChatBot service.
    if not temperature or not summary:
      raise exceptions.InvalidJSONFromAPIException("Forecast information not received from Datasky API.")

    forecast = "Currently it's %s F, %s." % (temperature, summary)

    return forecast

  def __call__(self, environ, start_response):
    """ A callable method called from the weather.wsgi application.

    Inputs:
      environ, A WSGI environ variable.
      start_response, A method to send the response back to the ChatBot service.

    Outputs:
      Weather forecast message back to the ChatBot service.

    Raises: 
      BadQueryException, InvalidJSONFromAPIException, ExternalAPIException depending on the exception being handled.
    """
    try:
      status = "200 OK"

      # Retrieve user input from POST request.
      output = self.ProcessClientRequest(environ)
    except exceptions.InvalidJSONFromAPIException as e:
      # Handled when there is no content in the responses from the public APIs.
      status = "204 No Content"
      output = e.message
    except exceptions.BadQueryException as e:
      # Handled when the request/ response doesn't contain the required data.
      status = "400 Bad Request"
      output = e.message
    except exceptions.ExternalAPIException as e:
      # Handled when the interaction with public APIs as not gone well.
      status = "500 Internal Server Error"
      output = e.message

    rsp_format = {
                   "message" : output
                 }

    # Format a response back to the ChatBot service.
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


