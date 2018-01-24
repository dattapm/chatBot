""" WSGI application for Weather API.
    This wil act as a middleware between the Apache web server and
    the Weather python application.
"""


import sys
sys.path.append('/opt/lessenger')

from weather.weather import Weather

# This will call the callable method in Weather API module.
application = Weather()
