#
#!/usr/bin/python
#

"""Generic exceptions and auxiliary functions to handle exception."""

import cgitb
import xml.sax.saxutils as saxutils

# Additional characters that need to be escaped for HTML defined in a dictionary
# the character to its escape string.
# xml.sax.saxutils.escape() takes care of &, < and >.
_HTML_ESCAPE_TABLE = {
    '"': "&quot;",
    "'": "&apos;"
    }


def HtmlEscape(text):
  """Escapes a string for HTML.

  Args:
    text: source string that needs to be escaped for HTML.
  Returns:
    HTML escaped string.
  """
  return saxutils.escape(text, _HTML_ESCAPE_TABLE)


def FormatException(exc_info):
  """Gets information from exception info tuple.

  Args:
    exc_info: exception info tuple (type, value, traceback)
  Returns:
    exception description in a list - wsgi application response format.
  """
  return [cgitb.handler(exc_info)]


class Error(Exception):
  """Generic error."""

  def ToString(self, error_prefix):
    """Builds error message string escaping it for HTML.

    Args:
      error_prefix: an error prefix.
    Returns:
      HTML escaped error message.
    """
    if error_prefix:
      return HtmlEscape("{0}: {1}".format(
          error_prefix,
          str(self.args[0] if len(self.args) <= 1 else self.args)))
    else:
      return HtmlEscape("Error: {0}".format(
          str(self.args[0] if len(self.args) <= 1 else self.args)))

  def __str__(self):
    return self.ToString("Error")

# Bad User query exception.
class BadQueryException(Error):
  """BadQueryException error."""

  def __str__(self):
    return self.ToString("BadQueryException")

# Invalid JSON request received by APIs.
class InvalidJSONFromAPIException(Error):
  """InvalidJSONFromAPIException error."""

  def __str__(self):
    return self.ToString("InvalidJSONFromAPIException")

# HTTPRequestException errors.
class HTTPRequestException(Error):
  """HTTPRequestException error."""

  def __str__(self):
    return self.ToString("HTTPRequestException")

# UnsupportedMediaTypeException errors.
class UnsupportedMediaTypeException(Error):
  """UnsupportedMediaTypeException error."""

  def __str__(self):
    return self.ToString("UnsupportedMediaTypeException")

def main():
  pass

if __name__ == "main":
  main()
