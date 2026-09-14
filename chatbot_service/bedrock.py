import os

import boto3
from botocore.config import Config

MODEL_ID = os.environ.get('CHATBOT_MODEL_ID', 'amazon.nova-micro-v1:0')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

MAX_MESSAGE_LENGTH = 500

_POLICY_PATH = os.path.join(os.path.dirname(__file__), 'policy.md')
with open(_POLICY_PATH, encoding='utf-8') as f:
    _POLICY_TEXT = f.read()

SYSTEM_PROMPT = (
    "You are a policy assistant for StaffRoom, an internal team "
    "discussion forum. Visitors ask you questions about the platform's "
    "rules of use. Answer using only the policy below, in plain, "
    "friendly language. If a question isn't covered by the policy, or "
    "is unrelated to StaffRoom's policies, say you can only help with "
    "questions about StaffRoom's rules of use — don't guess. You never "
    "take any action and never discuss a specific account or user, "
    "only general policy questions.\n\n" + _POLICY_TEXT
)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = boto3.client(
            'bedrock-runtime',
            region_name=AWS_REGION,
            config=Config(retries={'max_attempts': 3, 'mode': 'adaptive'}),
        )
    return _client


def _to_bedrock_messages(history, message):
    messages = []
    for item in history:
        role = item.get('role')
        text = (item.get('text') or '')[:MAX_MESSAGE_LENGTH]
        if role in ('user', 'assistant') and text:
            messages.append({'role': role, 'content': [{'text': text}]})
    messages.append({'role': 'user', 'content': [{'text': message[:MAX_MESSAGE_LENGTH]}]})
    return messages


def answer(message, history):
    """Returns a reply string, or None if the model produced no text."""
    response = _get_client().converse(
        modelId=MODEL_ID,
        system=[{'text': SYSTEM_PROMPT}],
        messages=_to_bedrock_messages(history, message),
        inferenceConfig={'maxTokens': 400, 'temperature': 0.2},
    )

    content = response.get('output', {}).get('message', {}).get('content', [])
    for block in content:
        text = block.get('text')
        if text:
            return text

    return None
