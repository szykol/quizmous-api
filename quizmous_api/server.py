from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS, cross_origin
from .db import DB, select_model_from_db, insert_model_to_db
from .version import get_api_version
from .api.swagger.models.quiz import Quiz
import jwt

app = Sanic()
CORS(app)
DBNAME = app.config['DBNAME'] if "DBNAME" in app.config else 'quiz' 
DSN = 'postgres://api:foobar@postgres_api:5432/{}'.format(DBNAME)
VERSION = get_api_version()

@app.route("/", methods=['GET', 'OPTIONS'])
async def test(request):
    body = {"name": "quizmous_api"}
    body.update(VERSION)
    return json(body=body, status=200)

@app.route("/quiz", methods=['GET', 'OPTIONS'])
async def get_quiz(request):
    await DB.init(dsn=DSN)
    quizes = await select_model_from_db(Quiz)

    return json(body=[q.to_dict() for q in quizes], status=200)
