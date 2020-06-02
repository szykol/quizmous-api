from enum import Enum
from sanic import response

class Responses(Enum):
    OK = {
        "status": 200,
        "message": "success"
    }

    BAD_REQUEST = {
        "status": 400,
        "message": "bad request"
    }

    UNAUTHORIZED = {
        "status": 401,
        "message": "user not authorized"
    }

    CREATED = {
        "status": 201,
        "message": "created"
    }

    INTERNAL = {
        "status": 500,
        "message": "internal server error"
    }

    UNIQUE_VIOLATED = {
        "status": 409,
        "message": "the data provided to endpoint already exists in the system"
    }

def create_response(resp: Responses, add: dict={}) -> response.HTTPResponse:
    """Generates response

    :param resp: Response enum
    :type resp: Responses
    :param add: additional response data, defaults to {}
    :type add: dict, optional
    :return: Sanic HTTPResponse
    :rtype: response.HTTPResponse
    """
    body = {"message": resp.value["message"]}
    body.update(add)
    return response.json(body=body, status=resp.value["status"])