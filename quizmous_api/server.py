from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS, cross_origin
from .db import DB
from .version import get_api_version
from .api.swagger.models.question import Question
from .api.swagger.models.quiz import Quiz
from .api.swagger.models.question_type import QuestionType

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
    
    quizes = await DB.get_pool().fetch(""" SELECT * FROM quiz """)
    quizes = [dict(q) for q in quizes]
    for quiz in quizes:
        questions = await DB.get_pool().fetch(""" SELECT * FROM quiz_question WHERE quiz_id=$1""", quiz["quiz_id"])
        questions = [dict(q) for q in questions]
        for question in questions:
            answers = await DB.get_pool().fetch(""" SELECT * FROM quiz_answer WHERE question_id=$1""", question["question_id"])
            answers = [dict(a) for a in answers]
            question["answers"] = answers
            question["type"] = QuestionType.from_dict(question["type"])
        quiz["questions"] = questions
        author = await DB.get_pool().fetch(""" SELECT user_id, nick from users WHERE user_id=$1 """, quiz["author"])
        quiz["author"] = dict(author[0])

    # Validate returned object is correct
    quizes = [Quiz.from_dict(quiz) for quiz in quizes]
    return json(body=[quiz.to_dict() for quiz in quizes], status=200)
