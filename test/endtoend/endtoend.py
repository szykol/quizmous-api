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

API_PORT=8000
API_URL = 'http://localhost:8000/'
DSN = 'postgres://api:foobar@postgres_api:5432/_test'

class EndpointBase(unittest.TestCase):
    def setUp(self):
        self._restart_test_db()
        
        self.coverage = os.getenv('API_TEST') == "coverage"
        if not self.coverage:
            self.sb = subprocess.Popen('/usr/local/api/api.py')
        
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

class EndpointTest(EndpointBase):
    def test_root(self):
        r = requests.get('http://localhost:8000/')
        payload = r.json()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(payload["name"], "quizmous_api")
        self.assertRegex(payload["version"], r"^(\d+\.)?(\d+\.)?(\*|\d+)$")

    def test_db_endpoint(self):
        r = requests.get('http://localhost:8000/db_test')
        self.assertEqual(r.status_code, 200)
        payload = r.json()
        
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(""" SELECT * FROM quiz_question WHERE quiz_id=1 """)
        questions = cur.fetchall()
        questions = [dict(q) for q in questions]
        self.assertEqual(payload['questions'], questions)
