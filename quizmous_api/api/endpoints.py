from sanic import Sanic
from sanic.response import json
import random

from quizmous_api import app, DSN, VERSION, SERIAL, Quiz, GetUser, PostUser, UserAnswers
from quizmous_api.db import DB, select_model_from_db, insert_model_to_db, insert_user_answers_to_db, insert_user_quiz_taken, select_user_quiz_taken
from quizmous_api.common import extract_jwt, parse_jwt

@app.route("/", methods=['GET', 'OPTIONS'])
@app.route("/version", methods=['GET', 'OPTIONS'])
async def test(request):
    """Returns api version

    :param request: request from user
    :type request: Request
    """
    body = {"name": "quizmous_api"}
    body.update(VERSION)
    return json(body=body, status=200)

@app.route("/quiz", methods=['GET', 'OPTIONS'])
@parse_jwt
async def get_quiz(payload):
    """Returns quiz

    :param payload: payload from user
    :type payload: Payload data
    """
    quizes = await select_model_from_db(Quiz)

    return json(body=[q.to_dict() for q in quizes], status=200)

@app.route("/quiz", methods=['POST'])
@parse_jwt
async def add_quiz(payload):
    """Adds a new quiz

    :param payload: payload from user
    :type payload: Payload data
    """
    quiz = Quiz.from_dict(payload)
    quiz_id = await insert_model_to_db(quiz)

    return json(body={"message": "success", "quiz_id": quiz_id}, status=201)

@app.route("/quiz/<id:int>", methods=['GET'])
@parse_jwt
async def get_quiz_by_id(payload, id: int):
    """Returns quiz by id

    :param payload: payload from user
    :type payload: Payload data
    :param id: id of quiz
    :type id: int
    """
    quizes = await select_model_from_db(Quiz, id)
    if quizes:
        return json(body=quizes[0].to_dict(), status=200)
    else:
        return json(body={"message": "Quiz with id: {} not found".format(id)}, status=400)

@app.route("/quiz/<id:int>", methods=['DELETE'])
@parse_jwt
async def delete_quiz(payload, id: int):
    """Deletes specific quiz by id

    :param payload: payload from user
    :type payload: Payload data
    :param id: id of quiz
    :type id: int
    """
    await DB.get_pool().execute(""" DELETE FROM quiz WHERE quiz_id = $1 """, id)

    return json(body={"message": "successful deletion"})

@app.route("/quiz", methods=['PUT'])
@parse_jwt
async def update_quiz(payload):
    """Updates quiz

    :param payload: payload from user
    :type payload: Payload data
    """
    quiz = Quiz.from_dict(payload)

    await DB.get_pool().execute(""" DELETE FROM quiz WHERE quiz_id = $1 """, quiz.quiz_id)
    quiz_id = await insert_model_to_db(quiz)

    return json(body={"message": "successful operation", "quiz_id": quiz_id})

@app.route("/user/register", methods=['POST'])
@parse_jwt
async def create_user(payload):
    """Creates a new user

    :param payload: payload from user
    :type payload: Payload data
    """
    user = PostUser.from_dict(payload)
    user_id = await insert_model_to_db(user)

    created_user = await select_model_from_db(GetUser, user_id)
    return json(body={"message": "user registered successfuly", "user": created_user.to_dict()}, status=201)

@app.route("/user/login", methods=['POST'])
@parse_jwt
async def login_user(payload):
    """Logs user

    :param payload: payload from user
    :type payload: Payload data
    """
    user = PostUser.from_dict(payload)
    result = await DB.get_pool().fetchrow(""" SELECT user_id, is_admin FROM users WHERE nick=$1 AND password=$2 """, user.nick, user.password)

    if result:
        # created_user = await select_model_from_db(GetUser, result["user_id"])
        return json(body={"message": "successful operation", "user": {"nick": user.nick, "user_id": result["user_id"], "is_admin": result["is_admin"]}}, status=200)
    return json(body={"message": "Invalid username/password supplied"}, status=400)

@app.route("/user/logout", methods=['POST'])
@parse_jwt
async def logout_user(payload):
    """Logs user

    :param payload: payload from user
    :type payload: Payload data
    """

    user = PostUser.from_dict(payload)
    result = await DB.get_pool().fetchrow(""" SELECT 1 FROM users WHERE nick=$1 AND password=$2 """, user.nick, user.password)

    if result:
        return json(body={"message": "successful operation"}, status=200)
    return json(body={"message": "Invalid username/password supplied"}, status=400)

@app.route("/quiz/<id:int>/answers", methods=['POST'])
@parse_jwt
async def insert_answers_for_quiz(payload, id: int):
    """Insert user answers for quiz

    :param payload: payload from user
    :type payload: Payload data
    :param id: id of quiz
    :type id: int
    """
    quiz_answers = payload
    result = await DB.get_pool().fetchrow(""" SELECT 1 FROM quiz WHERE quiz_id=$1""", id)

    if not result:
        return json(body={"message": "Invalid quiz id supplied"}, status=400)

    await insert_user_answers_to_db(quiz_answers, id)
    return json(body={"message": "answers inserted sucessfuly"}, status=201)


@app.route("/user/quiz_taken/<id:int>", methods=['POST'])
@parse_jwt
async def insert_quiz_taken(payload, id: int):
    """Insert data that user has taken the quiz

    :param payload: payload from user
    :type payload: Payload data
    :param id: id of quiz
    :type id: int
    """
    user = PostUser.from_dict(payload)
    result = await DB.get_pool().fetchrow(""" SELECT 1 FROM users WHERE nick=$1 AND password=$2 """, user.nick, user.password)

    if not result:
        return json(body={"message": "Invalid username/password supplied"}, status=400)

    await insert_user_quiz_taken(user, id)
    return json(body={"message": "quiz taken sucessfuly"}, status=201)

@app.route("/user/<user_nick:string>/quiz_taken/<id:int>", methods=['GET'])
@parse_jwt
async def get_quiz_taken(payload, user_nick: str, id: int):
    """Insert data that user has taken the quiz

    :param payload: payload from user
    :type payload: Payload data
    :param user_nick: nick of user
    :type user_nick: str
    :param id: id of quiz
    :type id: int
    """
    # user = PostUser.from_dict(payload)
    result = await DB.get_pool().fetchrow(""" SELECT 1 FROM users WHERE nick=$1""", user_nick)

    if not result:
        return json(body={"message": "Invalid username supplied"}, status=400)

    ret = await select_user_quiz_taken(user_nick, id)
    if ret:
        return json(body={"message": "quiz has been taken by user", "taken": True}, status=200)
    return json(body={"message": "quiz has not been taken by user", "taken": False}, status=200)

@app.route("/check_token", methods=['POST'])
@parse_jwt
async def get_answers_via_token(payload):
    """Returns answers using token provided by the user

    :param payload: payload from user
    :type payload: Payload data
    """

    token = payload["token"]
    print(token)
    row = await DB.get_pool().fetchrow(""" SELECT quiz_id, key_id FROM quiz_key WHERE key=$1""", token)

    if not row:
        return json(body={"message": "token not found"}, status=404)

    quiz_id  = row["quiz_id"]

    answers = await DB.get_pool().fetch(""" SELECT a.value, a.question_id,  qa.answer, qu.question FROM quiz_user_answers a left outer join quiz_answer qa on a.answer_id=qa.answer_id JOIN quiz_question qu on a.question_id=qu.question_id WHERE key_id=$1""", row["key_id"])
    
    questions = {}
    for answer in answers:
        question_id = answer["question_id"]
        if question_id not in questions:
            questions[question_id] = {
                "question": answer["question"],
                "answers": [answer["answer"] or answer["value"]]
            }
        else:
            questions[question_id]["answers"].append(answer["answer"] or answer["value"])
    
    return json(body={"message": "success", "answers": {"quiz_id": quiz_id, "questions": questions}}, status=200)

@app.route("/quiz/<id:int>/all_answers", methods=['POST'])
@parse_jwt
async def get_all_answers(payload, id):
    """Returns all answers for quiz if user is an admin

    :param payload: payload from user
    :type payload: Payload data
    :param id: id of quiz
    :type id: int
    """
    user = PostUser.from_dict(payload)
    result = await DB.get_pool().fetchrow(""" SELECT user_id, is_admin FROM users WHERE nick=$1 AND password=$2 """, user.nick, user.password)

    if not result:
        # created_user = await select_model_from_db(GetUser, result["user_id"])
        return json(body={"message": "Invalid username/password supplied"}, status=400)
    
    result = await DB.get_pool().fetchrow(""" SELECT quiz_id FROM quiz WHERE quiz_id=$1 """, id)
    if not result:
        # created_user = await select_model_from_db(GetUser, result["user_id"])
        return json(body={"message": "Invalid quiz_id supplied"}, status=404)

    user_ids = await DB.get_pool().fetch(""" SELECT user_id from user_quiz_taken WHERE quiz_id=$1""", id)
    user_ids = [row["user_id"] for row in user_ids]
    
    user_ids = random.sample(user_ids, len(user_ids))

    answers = await DB.get_pool().fetch(""" SELECT a.value, a.question_id,  qa.answer, qu.question FROM quiz_user_answers a left outer join quiz_answer qa on a.answer_id=qa.answer_id JOIN quiz_question qu on a.question_id=qu.question_id WHERE quiz_id=$1""", id)
    
    questions = {}
    for answer in answers:
        question_id = answer["question_id"]
        if question_id not in questions:
            questions[question_id] = {
                "question": answer["question"],
                "answers": [answer["answer"] or answer["value"]]
            }
        else:
            questions[question_id]["answers"].append(answer["answer"] or answer["value"])
    
    for key in questions.keys():
        questions[key]["answers"] = random.sample(questions[key]["answers"], len(questions[key]["answers"]))

    return json(body={"message": "success", "user_ids": user_ids, "questions": questions}, status=200)


def init_endpoints(app):
    """Initializes endpoint for app

    :param app: Sanic app
    :type app: Sanic App
    """
    app.add_route(test, '/', methods=['GET'])
    app.add_route(add_quiz, '/quiz', methods=['POST'])
    app.add_route(get_quiz, '/quiz', methods=['GET'])
