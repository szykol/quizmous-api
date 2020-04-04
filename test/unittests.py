from unittest import TestCase, mock
import asynctest
from sanic import response, request
import asyncpg
from ddt import ddt, data, unpack
import os, sys
import pytest
import json

from src.response import Responses, create_response
from src.db import DB
from src.server import app, test, db_test

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
    @mock.patch('src.db.db.asyncpg.create_pool', new_callable=mock.AsyncMock)
    async def test_create_pool(self, mockpg):
        DSN = 'unit://unit:unit@unit:5432/_unit'
        await DB.init(dsn=DSN)
        mockpg.assert_called_with(dsn=DSN)

    @mock.patch('src.db.db.asyncpg.create_pool', new_callable=mock.AsyncMock)
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
    
    @mock.patch('src.db.db.asyncpg.pool.Pool.execute', new_callable=mock.AsyncMock)
    async def test_test_db_endpoint(self, mock_execute):
        mock_request = mock.Mock(request.Request)
        resp = await db_test(mock_request)

        self.assertIsNotNone(resp) 
        self.assertIsInstance(resp, response.HTTPResponse)

        payload = json.loads(resp.body)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['status'], 'ok')
        self.assertEqual(resp.status, 200)

        mock_execute.assert_called_with(""" INSERT INTO dummy_tbl (name) VALUES ($1) """, "quizmous_api")

if __name__ == "__main__":
    unittest.main()
