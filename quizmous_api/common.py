import jwt
from jwt.exceptions import InvalidSignatureError, DecodeError
from typing import Union, Tuple

def extract_jwt(token: Union[str, bytes], serial: Union[str, bytes]) -> Tuple[bool, dict]:
    try:
        payload = jwt.decode(token, serial, algorithm='HS256')
        return (True, payload)
    except (InvalidSignatureError, DecodeError):
        return (False, None)

