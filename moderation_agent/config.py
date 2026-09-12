import os
import sys

REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
MODERATION_QUEUE_NAME = os.environ.get('MODERATION_QUEUE_NAME', 'moderation_queue')
MODERATION_HEARTBEAT_KEY = os.environ.get('MODERATION_HEARTBEAT_KEY', 'moderation_agent:heartbeat')
MODERATION_API_BASE_URL = os.environ.get('MODERATION_API_BASE_URL', 'http://localhost:5000')
MODERATION_SERVICE_TOKEN = os.environ.get('MODERATION_SERVICE_TOKEN')

if not MODERATION_SERVICE_TOKEN:
    sys.exit('MODERATION_SERVICE_TOKEN is not set; refusing to start.')
