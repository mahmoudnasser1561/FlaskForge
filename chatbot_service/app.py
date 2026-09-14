import logging

from flask import Flask, jsonify, request

import bedrock
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('chatbot-service')

app = Flask(__name__)


def _authorized(req):
    return req.headers.get('X-Chatbot-Token') == config.CHATBOT_SERVICE_TOKEN


@app.route('/health')
def health():
    return jsonify(status='ok')


@app.route('/answer', methods=['POST'])
def answer():
    if not _authorized(request):
        log.warning('rejected request with invalid or missing token')
        return jsonify(status='error', message='invalid token'), 401

    body = request.get_json(silent=True) or {}
    message = body.get('message', '')
    history = body.get('history') or []
    if not message:
        return jsonify(status='error', message='message is required'), 400
    log.info('received message: %r', message[:80])

    try:
        reply = bedrock.answer(message, history)
    except Exception as e:
        log.warning('bedrock call failed: %s', e)
        return jsonify(status='error', message='the model call failed'), 502

    if not reply:
        return jsonify(status='error', message='empty reply from model'), 502

    return jsonify(reply=reply)


if __name__ == '__main__':
    log.info('Chatbot service started')
    app.run(host='0.0.0.0', port=5001)
