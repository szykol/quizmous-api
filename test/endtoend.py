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

API_PORT=8000
API_URL = 'http://localhost:8000/'

class EndpointBase(unittest.TestCase):
    def setUp(self):
        self.sb = subprocess.Popen('/usr/local/api/src/main.py')
        self._wait_for_port()

    def tearDown(self):
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
