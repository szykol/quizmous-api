import jwt
from .version import get_api_version
from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS, cross_origin
import toml
from .response import create_response, Responses
from .common import extract_jwt

from quizmous_api.api.swagger.models.quiz import Quiz
from quizmous_api.api.swagger.models.answer import Answer
from quizmous_api.api.swagger.models.question import Question
from quizmous_api.api.swagger.models.question_type import QuestionType
from quizmous_api.api.swagger.models.get_user import GetUser

app = Sanic()
CORS(app)
DBNAME = app.config['DBNAME'] if "DBNAME" in app.config else 'quiz' 
DSN = 'postgres://api:foobar@postgres_api:5432/{}'.format(DBNAME)
VERSION = get_api_version()
SERIAL = 'serial' if "DBNAME" in app.config else toml.load('/usr/local/api/secrets.toml')['serial']

# def add_middleware():
#     @app.middleware('request')
#     async def parse_jwt_request(request):
#         if request.url != '/':
#             ok, payload = extract_jwt(request.body, SERIAL)
#             if ok:
#                 request.body = payload
#             else:
#                 return create_response(Responses.UNAUTHORIZED)


# app.add_task(add_middleware)