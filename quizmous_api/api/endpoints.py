from sanic import Sanic
from sanic.response import json

from quizmous_api import app, DSN, VERSION, SERIAL, Quiz, GetUser, PostUser
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
    quiz_id = await insert_model_to_db(quiz)

    return json(body={"message": "success", "quiz_id": quiz_id}, status=201)

@app.route("/quiz/<id:int>", methods=['GET'])
@parse_jwt
async def get_quiz_by_id(payload, id: int):
    quizes = await select_model_from_db(Quiz, id)
    quiz = quizes[0]

    return json(body=quiz.to_dict(), status=200)

@app.route("/quiz/<id:int>", methods=['DELETE'])
@parse_jwt
async def delete_quiz(payload, id: int):
    await DB.get_pool().execute(""" DELETE FROM quiz WHERE quiz_id = $1 """, id)

    return json(body={"message": "successful deletion"})

@app.route("/quiz", methods=['PUT'])
@parse_jwt
async def update_quiz(payload):
    quiz = Quiz.from_dict(payload)

    await DB.get_pool().execute(""" DELETE FROM quiz WHERE quiz_id = $1 """, quiz.quiz_id)
    quiz_id = await insert_model_to_db(quiz)

    return json(body={"message": "successful operation", "quiz_id": quiz_id})

@app.route("/user/register", methods=['POST'])
@parse_jwt
async def create_user(payload):
    user = PostUser.from_dict(payload)
    user_id = await insert_model_to_db(user)

    return json(body={"message": "user registered successfuly", "user_id": user_id}, status=201)

@app.route("/user/login", methods=['POST'])
@parse_jwt
async def login_user(payload):
    user = PostUser.from_dict(payload)
    result = await DB.get_pool().fetchrow(""" SELECT 1 FROM users WHERE nick=$1 AND password=$2 """, user.nick, user.password)

    if result:
        return json(body={"message": "successful operation"}, status=200)
    return json(body={"message": "Invalid username/password supplied"}, status=400)

@app.route("/user/logout", methods=['POST'])
@parse_jwt
async def logout_user(payload):
    user = PostUser.from_dict(payload)
    result = await DB.get_pool().fetchrow(""" SELECT 1 FROM users WHERE nick=$1 AND password=$2 """, user.nick, user.password)

    if result:
        return json(body={"message": "successful operation"}, status=200)
    return json(body={"message": "Invalid username/password supplied"}, status=400)


def init_endpoints(app):
    app.add_route(test, '/', methods=['GET'])
    app.add_route(add_quiz, '/quiz', methods=['POST'])
    app.add_route(get_quiz, '/quiz', methods=['GET'])
