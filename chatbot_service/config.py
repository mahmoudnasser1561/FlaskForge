import os
import sys

CHATBOT_SERVICE_TOKEN = os.environ.get('CHATBOT_SERVICE_TOKEN')

if not CHATBOT_SERVICE_TOKEN:
    sys.exit('CHATBOT_SERVICE_TOKEN is not set; refusing to start.')
