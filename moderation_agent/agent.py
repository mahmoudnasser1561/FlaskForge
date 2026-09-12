import logging

import redis
import requests

import config
from job import InvalidJobError, parse_job

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('moderation-agent')

HEARTBEAT_TTL = 20
POP_TIMEOUT = 5
REQUEST_TIMEOUT = 5


def refresh_heartbeat(client):
    client.set(config.MODERATION_HEARTBEAT_KEY, '1', ex=HEARTBEAT_TTL)


def _endpoint(job, action):
    kind = 'posts' if job.type == 'post' else 'comments'
    return f'{config.MODERATION_API_BASE_URL}/api/v1/moderation/{kind}/{job.id}/{action}'


def _headers():
    return {'X-Moderation-Token': config.MODERATION_SERVICE_TOKEN}


def call_verify(job):
    try:
        resp = requests.post(_endpoint(job, 'verify'),
                             json={'content_hash': job.content_hash},
                             headers=_headers(), timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        log.warning('verify request failed for %s %s: %s', job.type, job.id, e)
        return None
    if resp.status_code == 401:
        log.error('verify rejected: invalid moderation service token')
        return None
    if resp.status_code >= 500:
        log.warning('verify returned %s for %s %s', resp.status_code, job.type, job.id)
        return None
    return resp.json().get('status')


def call_disable(job, reason):
    try:
        resp = requests.post(_endpoint(job, 'disable'),
                             json={'reason': reason, 'content_hash': job.content_hash},
                             headers=_headers(), timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        log.warning('disable request failed for %s %s: %s', job.type, job.id, e)
        return None
    if resp.status_code == 401:
        log.error('disable rejected: invalid moderation service token')
        return None
    if resp.status_code >= 500:
        log.warning('disable returned %s for %s %s', resp.status_code, job.type, job.id)
        return None
    return resp.json().get('status')


def classify(job):
    return True, 'Flagged by the stub classifier (pipeline test, not a real policy decision)'


def process(job):
    verify_status = call_verify(job)
    if verify_status is None:
        return
    if verify_status == 'not_found':
        log.info('%s %s no longer exists, skipping', job.type, job.id)
        return
    if verify_status == 'stale':
        log.info('%s %s changed since queued, skipping', job.type, job.id)
        return

    flagged, reason = classify(job)
    if not flagged:
        log.info('%s %s not flagged', job.type, job.id)
        return

    disable_status = call_disable(job, reason)
    if disable_status is None:
        return
    if disable_status == 'disabled':
        log.info('%s %s disabled: %s', job.type, job.id, reason)
    elif disable_status == 'not_found':
        log.info('%s %s deleted before disable, skipping', job.type, job.id)
    elif disable_status == 'stale_skipped':
        log.info('%s %s changed before disable, skipping', job.type, job.id)
    elif disable_status == 'already_disabled':
        log.info('%s %s already disabled', job.type, job.id)
    else:
        log.warning('unexpected disable status %r for %s %s', disable_status, job.type, job.id)


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
        process(job)


if __name__ == '__main__':
    main()
