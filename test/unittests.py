import unittest
from unittest import TestCase, mock
import asynctest
from sanic import response, request
import asyncpg
from ddt import ddt, data, unpack
import os, sys
import pytest
import json

# force the app to not use secrets.toml file
os.environ["SANIC_DBNAME"] = "_test"

from quizmous_api.response import Responses, create_response
from quizmous_api.db import DB, insert_model_to_db
from quizmous_api.server import app
from quizmous_api.api.endpoints import test, get_quiz
from quizmous_api.version import get_api_version
from quizmous_api import Quiz, Answer, Question, QuestionType, GetUser

class UnitTestsBase(TestCase):
    def setUp(self):
        return super().setUp()

    def tearDown(self):
        return super().tearDown()

@ddt
class ResponseUnitTest(UnitTestsBase):
    @data(*[response for response in Responses])
    def test_create_response_returns_correct_type(self, input_response):
        resp = create_response(input_response)
        self.assertIsInstance(resp, response.HTTPResponse)

    @data(*[response for response in Responses])
    def test_create_response_correct_status(self, input_response):
        resp = create_response(input_response)
        self.assertEqual(resp.status, input_response.value["status"])

class AsyncDBUnitTest(asynctest.TestCase):
    @mock.patch('quizmous_api.db.asyncpg.create_pool', new_callable=mock.AsyncMock)
    async def test_create_pool(self, mockpg):
        DSN = 'unit://unit:unit@unit:5432/_unit'
        await DB.init(dsn=DSN)
        mockpg.assert_called_with(dsn=DSN)

    @mock.patch('quizmous_api.db.asyncpg.create_pool', new_callable=mock.AsyncMock)
    async def test_get_pool(self, mockpg):
        DSN = 'unit://unit:unit@unit:5432/_unit'
        mocked_pool = mock.Mock(asyncpg.pool.Pool)
        mockpg.return_value = mocked_pool
        await DB.init(dsn=DSN)
        pool = DB.get_pool()
        self.assertIsNotNone(pool)
        self.assertIsInstance(pool, asyncpg.pool.Pool)

    async def test_get_pool_without_init(self):
        # simulate DB before init
        DB._pool = None
        pool = DB.get_pool()
        self.assertIsNone(pool)

class AsyncMainTest(asynctest.TestCase):
    async def test_root_endpoint(self):
        mock_request = mock.Mock(request.Request)

        resp = await test(mock_request)
        self.assertIsNotNone(resp) 
        self.assertIsInstance(resp, response.HTTPResponse)
        payload = json.loads(resp.body)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['name'], 'quizmous_api')
        self.assertRegex(payload["version"], r"^(\d+\.)?(\d+\.)?(\*|\d+)$")
        self.assertIsInstance(payload["build"], int)

    @pytest.mark.skip("Write tests for quiz endpoint with mocked db")
    @mock.patch('quizmous_api.db.asyncpg.pool.Pool.execute', new_callable=mock.AsyncMock)
    async def test_test_get_quiz_endpoint(self, mock_execute):
        mock_request = mock.Mock(request.Request)
        await get_quiz(mock_request)

        pytest.fail("Not done yet")

    @pytest.mark.skip("Write tests for quiz insertion mocked db")
    async def test_quiz_model_addition(self):
        answers = [Answer(0, 'I do'), Answer(1, 'I dont')]
        answers2 = [Answer(0, 'Not yet'), Answer(1, 'Already done'), Answer(2, 'I do not know')]
        questions = [Question(question="Hello", type=QuestionType.RADIO, required=True, answers=answers),
        Question(question="Hello2", type=QuestionType.CHOICE, required=False, answers=answers2)]
        quiz_model = Quiz(quiz_id=1, author=GetUser(1, 'admin'), name="Quiz", description="Quiz", questions=questions)
        await insert_model_to_db(quiz_model)
        

class AsyncVersionTest(UnitTestsBase):
    @mock.patch('quizmous_api.version.open') 
    @mock.patch('quizmous_api.version.load', new_callable=mock.MagicMock)
    def test_get_version(self, mockload, mockopen):
        # mock_dict = mock.Mock({"version": "0.0.10", "build": 25})
        mockload.return_value = {"version": "0.0.10", "build": 25}
        # mockload.return_value(mock_dict)
        version = get_api_version()
        mockopen.assert_called_with("/usr/local/api/version.json", "r")
        self.assertIsInstance(version, dict)
        self.assertRegex(version["version"], r"^(\d+\.)?(\d+\.)?(\*|\d+)$")
        self.assertIsInstance(version["build"], int)
        
        

if __name__ == "__main__":
    unittest.main()
