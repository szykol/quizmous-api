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

    def _send_put_request(self, URL, payload, response_code=200, wrap_payload=True):
        r = requests.put(URL, data=self._wrap_payload(payload) if wrap_payload else payload)
        
        self.assertIsNotNone(r.json())
        print(r.json())
        self.assertEqual(r.status_code, response_code)

        return r

    def _send_get_request(self, URL, params=None, headers=None, use_token=True, response_code=200):
        token = self._wrap_payload({})
        header = {'Authorization': 'Bearer {}'.format(token.decode('utf-8'))} if use_token else {}
        if headers:
            header.update(headers)

        r = requests.get(URL, headers=header, params=params)
        self.assertIsNotNone(r.json())
        self.assertEqual(r.status_code, response_code)

        return r
    
    def _send_delete_request(self, URL, params=None, headers=None, use_token=True, response_code=200):
        token = self._wrap_payload({})
        header = {'Authorization': 'Bearer {}'.format(token.decode('utf-8'))} if use_token else {}
        if headers:
            header.update(headers)

        r = requests.delete(URL, headers=header, params=params)
        self.assertIsNotNone(r.json())
        self.assertEqual(r.status_code, response_code)

        return r

    def _create_test_quiz(self):
        answers = [
            [Answer(answer="Yes"), Answer(answer="No"), Answer(answer="Maybe")],
            [Answer(answer="Winter"), Answer(answer="Summer"), Answer(answer="Autumn"), Answer(answer="Spring")]
        ]

        questions = [
            Question(question="Do you like quizes?", type=QuestionType.RADIO, answers=answers[0], required=True),
            Question(question="Which season do you like?", type=QuestionType.CHOICE, answers=answers[1], required=True)
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
        self._send_post_request('http://localhost:8000/quiz', payload=quiz.to_dict(), response_code=201)

        self.cur.execute("SELECT COUNT(*) FROM quiz")
        count = self.cur.fetchall()[0][0]
        self.assertGreater(count, 1)

    def test_get_quiz_endpoint(self):
        r = self._send_get_request('http://localhost:8000/quiz')
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
    
    def test_get_quiz_by_id_endpoint(self):
        r = self._send_get_request('http://localhost:8000/quiz/1')
        payload = r.json()
        self.maxDiff = None
        # Check if fits the model
        quiz_model = Quiz.from_dict(payload)

        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(""" SELECT * FROM quiz WHERE quiz_id = %s""", (1, ))
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
        
        self.assertEqual(payload, quizes[0])

    def test_delete_quiz(self):
        r = self._send_delete_request("http://localhost:8000/quiz/1")
        payload = r.json()

        self.assertEqual(payload["message"], 'successful deletion')

    def test_update_quiz(self):
        quiz = self._create_test_quiz()
        r = self._send_post_request('http://localhost:8000/quiz', payload=quiz.to_dict(), response_code=201)
        self.cur.execute("SELECT COUNT(*) FROM quiz WHERE name='Test Quiz'")
        count = self.cur.fetchall()[0][0]
        self.assertGreater(count, 0)

        payload = r.json()
        quiz_id = payload["quiz_id"]
        quiz.quiz_id = int(quiz_id)
        quiz.name = 'Updated quiz'

        r = self._send_put_request("http://localhost:8000/quiz", payload=quiz.to_dict(), response_code=200)
        self.cur.execute("SELECT COUNT(*) FROM quiz WHERE name='Updated quiz'")
        count = self.cur.fetchall()[0][0]
        self.assertGreater(count, 0)
        self.cur.execute("SELECT COUNT(*) FROM quiz WHERE name='Test Quiz'")
        count = self.cur.fetchall()[0][0]
        self.assertEqual(count, 0)