import jwt
from jwt.exceptions import InvalidSignatureError, DecodeError
from typing import Union, Tuple
from .response import Responses, create_response
import traceback
from quizmous_api import SERIAL
from sanic.request import Request
from sanic.response import json, HTTPResponse
from .db import UniqueModelConstraint

def extract_jwt(token: Union[str, bytes], serial: Union[str, bytes]) -> Tuple[bool, dict]:
    """Extracts jwt tokens

    :param token: token from request
    :type token: Union[str, bytes]
    :param serial: serial used to hash the token
    :type serial: Union[str, bytes]
    :return: Data saved in token
    :rtype: Tuple[bool, dict]
    """
    try:
        payload = jwt.decode(token, serial, algorithm='HS256')
        return (True, payload)
    except (InvalidSignatureError, DecodeError):
        return (False, None)

def parse_jwt(f):
    """Decorator that parses the token and returns it to decorated function
    """
    async def wrapper(request: Request, *args, **kwargs) -> HTTPResponse:
        token = extract_token(request)
        ok, payload = extract_jwt(token, SERIAL)
        if ok:
            try:
                return await f(payload, *args, **kwargs)
            except UniqueModelConstraint as e:
                return create_response(Responses.UNIQUE_VIOLATED, {"message": str(e)})
            except Exception as e:
                print(traceback.format_exc())
                return create_response(Responses.INTERNAL, {"traceback": traceback.format_exc()})
        else:
            return create_response(Responses.UNAUTHORIZED)
    return wrapper

def extract_token(request: Request) -> Union[bytes, str]:
    """Finds token in request based on it's type

    :param request: request from user
    :type request: Request
    :return: token
    :rtype: Union[bytes, str]
    """
    token = None
    if request.method in ['POST', 'PUT']:
        token = request.body
    else:
        header = request.headers.get('Authorization')
        if header:
            token = header.split(' ')[1]

    return token