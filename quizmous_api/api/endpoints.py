from sanic import Sanic
from sanic.response import json

from quizmous_api import app, DSN, VERSION, SERIAL, Quiz, GetUser, PostUser, UserAnswers
from quizmous_api.db import DB, select_model_from_db, insert_model_to_db, insert_user_answers_to_db, insert_user_quiz_taken, select_user_quiz_taken
from quizmous_api.common import extract_jwt, parse_jwt

@app.route("/", methods=['GET', 'OPTIONS'])
@app.route("/version", methods=['GET', 'OPTIONS'])
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
    if quizes:
        return json(body=quizes[0].to_dict(), status=200)
    else:
        return json(body={"message": "Quiz with id: {} not found".format(id)}, status=400)

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

    created_user = await select_model_from_db(GetUser, user_id)
    return json(body={"message": "user registered successfuly", "user": created_user.to_dict()}, status=201)

@app.route("/user/login", methods=['POST'])
@parse_jwt
async def login_user(payload):
    user = PostUser.from_dict(payload)
    result = await DB.get_pool().fetchrow(""" SELECT user_id FROM users WHERE nick=$1 AND password=$2 """, user.nick, user.password)

    if result:
        created_user = await select_model_from_db(GetUser, result["user_id"])
        return json(body={"message": "successful operation", "user": created_user.to_dict()}, status=200)
    return json(body={"message": "Invalid username/password supplied"}, status=400)

@app.route("/user/logout", methods=['POST'])
@parse_jwt
async def logout_user(payload):
    user = PostUser.from_dict(payload)
    result = await DB.get_pool().fetchrow(""" SELECT 1 FROM users WHERE nick=$1 AND password=$2 """, user.nick, user.password)

    if result:
        return json(body={"message": "successful operation"}, status=200)
    return json(body={"message": "Invalid username/password supplied"}, status=400)

@app.route("/quiz/<id:int>/answers", methods=['POST'])
@parse_jwt
async def insert_answers_for_quiz(payload, id: int):
    quiz_answers = payload
    result = await DB.get_pool().fetchrow(""" SELECT 1 FROM quiz WHERE quiz_id=$1""", id)

    if not result:
        return json(body={"message": "Invalid quiz id supplied"}, status=400)

    await insert_user_answers_to_db(quiz_answers)
    return json(body={"message": "answers inserted sucessfuly"}, status=201)


@app.route("/user/quiz_taken/<id:int>", methods=['POST'])
@parse_jwt
async def insert_quiz_taken(payload, id: int):
    user = PostUser.from_dict(payload)
    result = await DB.get_pool().fetchrow(""" SELECT 1 FROM users WHERE nick=$1 AND password=$2 """, user.nick, user.password)

    if not result:
        return json(body={"message": "Invalid username/password supplied"}, status=400)

    await insert_user_quiz_taken(user, id)
    return json(body={"message": "quiz taken sucessfuly"}, status=201)

@app.route("/user/<user_nick:string>/quiz_taken/<id:int>", methods=['GET'])
@parse_jwt
async def get_quiz_taken(payload, user_nick: str, id: int):
    # user = PostUser.from_dict(payload)
    result = await DB.get_pool().fetchrow(""" SELECT 1 FROM users WHERE nick=$1""", user_nick)

    if not result:
        return json(body={"message": "Invalid username supplied"}, status=400)

    ret = await select_user_quiz_taken(user_nick, id)
    if ret:
        return json(body={"message": "quiz has been taken by user", "taken": True}, status=200)
    return json(body={"message": "quiz has not been taken by user", "taken": False}, status=200)


def init_endpoints(app):
    app.add_route(test, '/', methods=['GET'])
    app.add_route(add_quiz, '/quiz', methods=['POST'])
    app.add_route(get_quiz, '/quiz', methods=['GET'])
