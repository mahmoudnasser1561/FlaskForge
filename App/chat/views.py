import requests
from flask import current_app, jsonify, request

from . import chat
from .. import limiter
from ..api.errors import bad_request

MAX_MESSAGE_LENGTH = 500
MAX_HISTORY_MESSAGES = 6
STATUS_TIMEOUT = (1, 2)
ANSWER_TIMEOUT = (2, 8)


def _service_configured():
    return bool(current_app.config['CHATBOT_SERVICE_URL']) and \
        bool(current_app.config['CHATBOT_SERVICE_TOKEN'])


def _service_url(path):
    return current_app.config['CHATBOT_SERVICE_URL'].rstrip('/') + path


def _unavailable():
    response = jsonify({'error': 'unavailable',
                        'message': 'The policy assistant is not available right now.'})
    response.status_code = 503
    return response


@chat.route('/chat/status')
def status():
    if not _service_configured():
        return jsonify(available=False)
    try:
        resp = requests.get(_service_url('/health'), timeout=STATUS_TIMEOUT)
    except requests.RequestException:
        return jsonify(available=False)
    return jsonify(available=resp.status_code == 200)


@chat.route('/chat', methods=['POST'])
@limiter.limit('20 per minute')
def send_message():
    body = request.get_json(silent=True) or {}
    message = (body.get('message') or '').strip()
    if not message:
        return bad_request('message is required')
    message = message[:MAX_MESSAGE_LENGTH]

    if not _service_configured():
        return _unavailable()

    cleaned_history = []
    for item in (body.get('history') or [])[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(item, dict):
            continue
        role = item.get('role')
        text = (item.get('text') or '').strip()[:MAX_MESSAGE_LENGTH]
        if role in ('user', 'assistant') and text:
            cleaned_history.append({'role': role, 'text': text})

    try:
        resp = requests.post(
            _service_url('/answer'),
            json={'message': message, 'history': cleaned_history},
            headers={'X-Chatbot-Token': current_app.config['CHATBOT_SERVICE_TOKEN']},
            timeout=ANSWER_TIMEOUT)
    except requests.RequestException:
        return _unavailable()

    if resp.status_code != 200:
        return _unavailable()

    try:
        reply = (resp.json() or {}).get('reply')
    except ValueError:
        reply = None
    if not reply:
        return _unavailable()

    return jsonify(reply=reply)
