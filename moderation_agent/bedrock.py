import os

import boto3
from botocore.config import Config

MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'amazon.nova-micro-v1:0')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

MAX_BODY_LENGTH = 4000

_POLICY_PATH = os.path.join(os.path.dirname(__file__), 'policy.md')
with open(_POLICY_PATH, encoding='utf-8') as f:
    _POLICY_TEXT = f.read()

SYSTEM_PROMPT = (
    'You are an automated content moderator for StaffRoom, an internal '
    'team discussion forum. You will be shown the text of a single post '
    'or comment. Decide whether it clearly violates the policy below. '
    'If it does, call the provided tool with a short, specific reason. '
    'If the content does not clearly match any category below — '
    'including genuinely ambiguous or borderline cases — do not call '
    'the tool, and reply with a brief acknowledgement instead. A missed '
    'violation is preferable to wrongly silencing legitimate content, '
    'so only flag when the match is clear.\n\n' + _POLICY_TEXT
)

_TOOL_NAMES = {
    'post': 'flag_post_content',
    'comment': 'flag_comment_content',
}

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


def _tool_config(kind):
    return {
        'tools': [
            {
                'toolSpec': {
                    'name': _TOOL_NAMES[kind],
                    'description': 'Flag this content as violating the moderation policy.',
                    'inputSchema': {
                        'json': {
                            'type': 'object',
                            'properties': {
                                'reason': {
                                    'type': 'string',
                                    'description': 'A short, specific explanation of which policy this content violates.',
                                },
                            },
                            'required': ['reason'],
                        }
                    },
                }
            }
        ]
    }


def classify(job):
    """Returns (flagged: bool, reason: str | None)."""
    body = job.body[:MAX_BODY_LENGTH]
    tool_name = _TOOL_NAMES[job.type]

    response = _get_client().converse(
        modelId=MODEL_ID,
        system=[{'text': SYSTEM_PROMPT}],
        messages=[{'role': 'user', 'content': [{'text': body}]}],
        toolConfig=_tool_config(job.type),
        inferenceConfig={'maxTokens': 300, 'temperature': 0},
    )

    content = response.get('output', {}).get('message', {}).get('content', [])
    for block in content:
        tool_use = block.get('toolUse')
        if not tool_use or tool_use.get('name') != tool_name:
            continue
        reason = (tool_use.get('input') or {}).get('reason')
        if not reason:
            continue
        return True, reason

    return False, None
