import jwt
from .version import get_api_version
from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS, cross_origin
import toml
from .response import create_response, Responses

from quizmous_api.api.swagger.models.quiz import Quiz
from quizmous_api.api.swagger.models.answer import Answer
from quizmous_api.api.swagger.models.question import Question
from quizmous_api.api.swagger.models.question_type import QuestionType
from quizmous_api.api.swagger.models.get_user import GetUser
from quizmous_api.api.swagger.models.post_user import PostUser
from quizmous_api.api.swagger.models.user_answers import UserAnswers

app = Sanic()
# CORS(app)
DBNAME = app.config['DBNAME'] if "DBNAME" in app.config else 'quiz' 
DSN = 'postgres://api:foobar@postgres_api:5432/{}'.format(DBNAME)
VERSION = get_api_version()
SERIAL = 'serial' if "DBNAME" in app.config else toml.load('/usr/local/api/secrets.toml')['serial']