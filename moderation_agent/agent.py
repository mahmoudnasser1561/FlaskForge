import logging

import redis

import config
from job import InvalidJobError, parse_job

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('moderation-agent')

HEARTBEAT_TTL = 20
POP_TIMEOUT = 5


def refresh_heartbeat(client):
    client.set(config.MODERATION_HEARTBEAT_KEY, '1', ex=HEARTBEAT_TTL)


def main():
    client = redis.Redis.from_url(config.REDIS_URL)
    log.info('Moderation agent started, watching queue %r', config.MODERATION_QUEUE_NAME)

    while True:
        refresh_heartbeat(client)
        item = client.brpop(config.MODERATION_QUEUE_NAME, timeout=POP_TIMEOUT)
        if item is None:
            continue

        _, raw = item
        try:
            job = parse_job(raw)
        except InvalidJobError as e:
            log.warning('Skipping malformed queue job: %s (raw=%r)', e, raw)
            continue

        log.info('Popped job: type=%s id=%s user_id=%s content_hash=%s',
                 job.type, job.id, job.user_id, job.content_hash)


if __name__ == '__main__':
    main()
