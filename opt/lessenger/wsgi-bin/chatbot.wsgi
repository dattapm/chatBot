""" WSGI application for ChatBot.
    This wil act as a middleware between the Apache web server and
    the ChatBot python application.
"""

import sys
sys.path.append('/opt/lessenger')

from chatbot.chatbot import ChatBot

# This will call the callable method in ChatBot module.
application = ChatBot()
