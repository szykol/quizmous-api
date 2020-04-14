from sanic import Sanic
from sanic.response import json

from quizmous_api import app, DSN, VERSION, SERIAL, Quiz
from quizmous_api.db import DB, select_model_from_db, insert_model_to_db
from quizmous_api.common import extract_jwt, parse_jwt

@app.route("/", methods=['GET', 'OPTIONS'])
async def test(request):
    body = {"name": "quizmous_api"}
    body.update(VERSION)
    return json(body=body, status=200)

@app.route("/quiz", methods=['GET', 'OPTIONS'])
@parse_jwt
async def get_quiz(payload):
    quizes = await select_model_from_db(Quiz)

    return json(body=[q.to_dict() for q in quizes], status=200)

@app.route("/quiz", methods=['POST'])
@parse_jwt
async def add_quiz(payload):
    quiz = Quiz.from_dict(payload)
    await insert_model_to_db(quiz)

    return json(body={"message": "success"}, status=201)

def init_endpoints(app):
    app.add_route(test, '/', methods=['GET'])
    app.add_route(add_quiz, '/quiz', methods=['POST'])
    app.add_route(get_quiz, '/quiz', methods=['GET'])
