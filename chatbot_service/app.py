import logging

from flask import Flask, jsonify, request

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
    log.info('received message: %r', message[:80])

    return jsonify(reply='This is a placeholder reply from the policy assistant.')


if __name__ == '__main__':
    log.info('Chatbot service started')
    app.run(host='0.0.0.0', port=5001)
