""" WSGI application for Welcome API.
    This wil act as a middleware between the Apache web server and
    the Welcome python application.
"""
import sys
sys.path.append('/opt/lessenger')

from welcome.welcome import Welcome

# This will call the callable method in Welcome API module.
application = Welcome()
