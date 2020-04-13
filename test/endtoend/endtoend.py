import unittest
import subprocess
import requests
import time
import pytest
import psycopg2
import os
import json
import jwt
import re
from urllib3.exceptions import NewConnectionError
from copy import deepcopy
from datetime import datetime
from psycopg2.extras import RealDictCursor

from quizmous_api import Quiz, Question, Answer, QuestionType, GetUser

API_PORT=8000
API_URL = 'http://localhost:8000/'
DSN = 'postgres://api:foobar@postgres_api:5432/_test'

class EndpointBase(unittest.TestCase):
    def setUp(self):
        self._restart_test_db()
        
        self.coverage = os.getenv('API_TEST') == "coverage"
        if not self.coverage:
            self.sb = subprocess.Popen('/usr/local/api/run.py')
        
        self._wait_for_port()
        self.conn = psycopg2.connect(DSN)
        self.cur = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

        if not self.coverage:
            self.sb.kill()

    def _wait_for_port(self, timeout=5, port=API_PORT):
        tout = time.monotonic() + timeout

        while time.monotonic() < tout:
            try:
                requests.get('http://localhost:{}/'.format(port))
            except Exception:
                time.sleep(0.1)
            else:
                return
        pytest.fail()

    def _restart_test_db(self):
        os.environ["SANIC_DBNAME"] = "_test"
        queries = ["DROP DATABASE IF EXISTS _test", "CREATE DATABASE _test" ]
        for q in queries:
            subprocess.call(['psql', '-c {}'.format(q)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        
        subprocess.call(['psql', '-d_test', '-a', '-f/usr/local/api/schema.sql'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def _wrap_payload(self, payload):
        return jwt.encode(payload, 'serial', algorithm='HS256')

    def _send_post_request(self, URL, payload, response_code=200, wrap_payload=True):
        r = requests.post(URL, data=self._wrap_payload(payload) if wrap_payload else payload)
        
        self.assertIsNotNone(r.json())
        self.assertEqual(r.status_code, response_code)

        return r

    def _create_test_quiz(self):
        answers = [
            [Answer(answer="Yes"), Answer(answer="No"), Answer(answer="Maybe")],
            [Answer(answer="Winter"), Answer(answer="Summer"), Answer(answer="Autumn"), Answer(answer="Spring")]
        ]

        questions = [
            Question(question="Do you like quizes?", type=QuestionType.RADIO, answers=answers[0]),
            Question(question="Which season do you like?", type=QuestionType.CHOICE, answers=answers[1])
        ]

        user = GetUser(user_id=1, nick='admin')
        quiz = Quiz(author=user, name='Test Quiz', description="Quiz for testing purposes", questions=questions)

        return quiz
class EndpointTest(EndpointBase):
    def test_root(self):
        r = requests.get('http://localhost:8000/')
        payload = r.json()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(payload["name"], "quizmous_api")
        self.assertRegex(payload["version"], r"^(\d+\.)?(\d+\.)?(\*|\d+)$")

    def test_add_quiz_endpoint(self):
        quiz = self._create_test_quiz()
        self._send_post_request('http://localhost:8000/quiz', payload=quiz.to_dict())

    def test_get_quiz_endpoint(self):
        r = requests.get('http://localhost:8000/quiz')
        self.assertEqual(r.status_code, 200)
        payload = r.json()
        self.maxDiff = None
        # Check if fits the model
        quiz_model = Quiz.from_dict(payload)

        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(""" SELECT * FROM quiz """)
        quizes = cur.fetchall()
        quizes = [dict(q) for q in quizes]
        for idx, quiz in enumerate(quizes):
            cur.execute(""" SELECT * FROM quiz_question WHERE quiz_id={}""".format(quiz["quiz_id"]))
            questions = cur.fetchall()
            questions = [dict(q) for q in questions]
            for question in questions:
                answers = cur.execute(""" SELECT * FROM quiz_answer WHERE question_id={}""".format(question["question_id"]))
                answers = cur.fetchall()
                answers = [dict(a) for a in answers]
                for answer in answers:
                    del answer["question_id"]
                question["answers"] = answers
                del question["quiz_id"]
            quiz["questions"] = questions
            author = cur.execute(""" SELECT user_id, nick from users WHERE user_id={} """.format(quiz["author"]))
            author = cur.fetchall()
            quiz["author"] = dict(author[0])
        
        self.assertEqual(payload, quizes)