import cgi
import json
import urllib
import urllib2

from common import exceptions

class Base(object):

  def __init__(self):
    self.server_url = "http://localhost:9000"
    self.api_headers = {
                        'Content-Type': 'application/json'
                       }

  def GetFormData(self, environ, api_name=None):
      # When the method is POST the variable will be sent
      # in the HTTP request body which is passed by the WSGI server
      # in the file like wsgi.input environment variable.

      form_data = {}

      content_type = environ.get("CONTENT_TYPE")
      if content_type:
        content_type_value, content_type_dict = cgi.parse_header(content_type)
        if content_type_value == "multipart/form-data":
          form_data = cgi.parse_multipart(environ["wsgi.input"], content_type_dict)
        elif content_type_value == "application/json":
          try:
            request_body_size = int(environ.get("CONTENT_LENGTH", 0))
          except (ValueError):
            request_body_size = 0
          
          try:
            request_body = environ["wsgi.input"].read(request_body_size)
            request_body = cgi.parse_qs(request_body)
            form_data = json.loads(request_body["json"][0])
          except:
            raise exceptions.InvalidJSONFromAPIException("Invalid JSON message received by '%s' API." %(api_name))  
        else:
          raise exceptions.UnsupportedMediaTypeException("%s Content-Type not supported." %(content_type_value))
      else:
        raise exceptions.HTTPRequestException("Content-Type header not found in HTTP environment.")

      return form_data

  def GetHTTPResponse(self, url_data, api_name):
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
      if hasattr(e, "code"):  # HTTPError
        if e.code == 500:
          raise exceptions.ServerNotAvailableException(e.message)
      elif hasattr(e, "reason"):  # URLError
        raise exceptions.UnknownException(e.reason)

      response = json.loads(cgi.parse_qs(e.read())["json"][0])
      raise exceptions.BadQueryException(response.get("message"))


  def GetExternalAPIResponse(self, url):
    try:
      response = urllib2.urlopen(url)
      rsp_from_external_api = json.loads(response.read())
    except urllib2.URLError as e:
      if hasattr(e, "code"):  # HTTPError
        if e.code == 500:
          raise exceptions.ServerNotAvailableException(e.message)
      elif hasattr(e, "reason"):  # URLError
        raise exceptions.UnknownException(e.reason)

    return rsp_from_external_api

  def __del__(self):
    pass
