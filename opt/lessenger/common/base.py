import cgi
import json
import urllib
import urllib2

from common import exceptions

class Base(object):
  """Base class has some common utility methods
  which are used by ChatBot service and Welcome and Weather APIs.
  """

  def __init__(self):
    self.server_url = "http://localhost:9000"
    self.api_headers = {
                         "Content-Type": "application/json;charset=UTF-8"
                       }

  def GetFormData(self, environ, api_name=None):
    """ This method will read the HTML form and
    retrieve the user entered form data.
       
    The process to read the form is based on the 
     Content-Type of the data received.

    Args:
      environ: A WSGI based environ variable.
      api_name: Either 'Welcome' or 'Weather'.
    Returns:
      form_data: A dict of form data.
    Raises:
       InvalidJSONFromAPIException, UnsupportedMediaTypeException, HTTPRequestException based on what is being handled.
    """
    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.

    form_data = {}

    content_type = environ.get("CONTENT_TYPE")
    if content_type:
      content_type_value, content_type_dict = cgi.parse_header(content_type)
      if content_type_value == "multipart/form-data":
        # This content type isused for communication between
        # ChatBot and lessenger UI.

        form_data = cgi.parse_multipart(environ["wsgi.input"], content_type_dict)
      elif content_type_value == "application/json":
        # This Content-Type is used for inter-communication between
        # ChatBot and Welcome/ Weather APIs.

        try:
          request_body_size = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError):
          request_body_size = 0
          
        # Read and parse the form data received from the HTTP request.
        try:
          request_body = environ["wsgi.input"].read(request_body_size)
          request_body = cgi.parse_qs(request_body)
          form_data = json.loads(request_body["json"][0])
        except:
          # Handled when the JSON message is not as per the format expected.
          raise exceptions.InvalidJSONFromAPIException("Invalid JSON message received by '%s' API." %(api_name))  
      else:
        # Handled when the content type received is not of the type supported.
        raise exceptions.UnsupportedMediaTypeException("%s Content-Type not supported." %(content_type_value))
    else:
      # Handled when the content type header field is not received in the HTTP request.
      raise exceptions.HTTPRequestException("Content-Type header not found in HTTP environment.")

    return form_data

  def GetHTTPResponse(self, url_data, api_name):
    """ This method is used to send and receive HTTP POST requests.

    This is used for cummunication between ChatBot and Welcome/ Weather APIs.

    Args:
      url_data: This is the data that is embedded into the HTTP POST message body.
      api_name: This is the api to which the HTTP request is being sent to.

    Returns:
      HTTP response received from the Welcome and Weather APIs.
    Raises:
      BadQueryException,InvalidJSONFromAPIException,ServerNotAvailableException, UnknownException based on what is 
      being handled.
    """
    try:
      data = urllib.urlencode({"json": json.dumps(url_data)})
      url = self.server_url + api_name
      request = urllib2.Request(url, data, self.api_headers)
      response = urllib2.urlopen(request)

      if response.getcode() == 204:
        raise exceptions.InvalidJSONFromAPIException("Invalid JSON message received by '%s' API." %(api_name))
      elif response.getcode() == 200:
        response = json.loads(cgi.parse_qs(response.read())["json"][0])

        # Check if the response from the API is valid.
        response_from_api = response.get("message")
        if not response or not response_from_api:
          raise exceptions.InvalidJSONFromAPIException("Invalid response received from %s API." %(api_name))

        return response_from_api
    except urllib2.URLError as e:
      response = json.loads(cgi.parse_qs(e.read())["json"][0])
      if hasattr(e, "code"):  # HTTPError
        if e.code == 500:
          # Handled when the public APIs(Google Geocoding and Datasky APIs are not responding)
          raise exceptions.ServerNotAvailableException(response.get("message"))
        elif e.code == 400:
          # Handled when the response sent by the public APIs(Google Geocoding and Datasky APIs are not valid)
          raise exceptions.BadQueryException(response.get("message"))
      elif hasattr(e, "reason"):  # URLError
        # Handled when any exception other than the one handled above occur.
        raise exceptions.UnknownException(e.reason)


  def GetExternalAPIResponse(self, url):
    """ This method is used to send and receive HTTP POST requests to public APIs. 

    This is used for cummunication between Weather API and Google Geocoding API and Datasky API.

    Args:
      url: URL of the public APIs to which the request need to be sent.
    Returns:
      HTTP response received from the public APIs.
    Raises:
      BadQueryException,ServerNotAvailableException, UnknownException based on what is being handled.
    """
    try:
      response = urllib2.urlopen(url)
      rsp_from_external_api = json.loads(response.read())
      return rsp_from_external_api
    except urllib2.URLError as e:
      response = json.loads(e.read())
      if hasattr(e, "code"):  # HTTPError
        if e.code == 500:
          # Handled when the public APIs(Google Geocoding and Datasky APIs are not responding)
          raise exceptions.ServerNotAvailableException(response.get("error_message"))
        elif e.code == 400:
          # Handled when the response sent by the public APIs(Google Geocoding and Datasky APIs are not valid)
          raise exceptions.BadQueryException(response.get("error_message"))
      elif hasattr(e, "reason"):  # URLError
        # Handled when any exception other than the one handled above occur.
        raise exceptions.UnknownException(e.reason)

  def __del__(self):
    pass
