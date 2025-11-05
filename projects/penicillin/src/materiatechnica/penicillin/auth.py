from typing import Optional

from flask_httpauth import HTTPTokenAuth

auth = HTTPTokenAuth(scheme="Bearer")

tokens = {"7cgU2MXoqpK0PDuCAmHMpROat": "application", "bzFY9GwC24qP8UN5Pma0gZb14": "backend"}


@auth.verify_token  # type:ignore[misc, return]
def verify_token(token: str) -> Optional[str]:
    if token in tokens:
        return tokens[token]
