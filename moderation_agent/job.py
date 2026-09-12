import json
from dataclasses import dataclass

REQUIRED_FIELDS = ('type', 'id', 'user_id', 'body', 'content_hash')


class InvalidJobError(Exception):
    pass


@dataclass(frozen=True)
class ModerationJob:
    type: str
    id: int
    user_id: int
    body: str
    content_hash: str


def parse_job(raw):
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise InvalidJobError(f'malformed JSON: {e}') from e

    if not isinstance(data, dict):
        raise InvalidJobError(f'expected a JSON object, got {type(data).__name__}')

    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        raise InvalidJobError(f'missing fields: {missing}')

    if data['type'] not in ('post', 'comment'):
        raise InvalidJobError(f"unknown type: {data['type']!r}")

    try:
        return ModerationJob(
            type=data['type'],
            id=int(data['id']),
            user_id=int(data['user_id']),
            body=str(data['body']),
            content_hash=str(data['content_hash']),
        )
    except (TypeError, ValueError) as e:
        raise InvalidJobError(f'bad field type: {e}') from e
