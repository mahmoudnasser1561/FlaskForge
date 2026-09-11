import hashlib
import json

import redis
from flask import current_app

_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(current_app.config['REDIS_URL'])
    return _redis_client


def queue_for_moderation(kind, obj):
    if not current_app.config.get('MODERATION_ENABLED', True):
        return
    try:
        client = _get_redis()
        if not client.exists(current_app.config['MODERATION_HEARTBEAT_KEY']):
            current_app.logger.info('AI moderation is not available; skipping.')
            return
        payload = json.dumps({
            'type': kind,
            'id': obj.id,
            'user_id': obj.author_id,
            'body': obj.body,
            'content_hash': hashlib.sha256(obj.body.encode('utf-8')).hexdigest(),
        })
        client.lpush(current_app.config['MODERATION_QUEUE_NAME'], payload)
    except redis.RedisError:
        current_app.logger.info('AI moderation is not available; skipping.')
