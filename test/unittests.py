from unittest import TestCase, mock
import asynctest
from sanic import response, request
from ddt import ddt, data, unpack
import os, sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.response import Responses, create_response
from src.db import DB, asyncpg

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
    @mock.patch('src.db.asyncpg.create_pool', new_callable=mock.AsyncMock)
    async def test_create_pool(self, mockpg):
        DSN = 'unit://unit:unit@unit:5432/_unit'
        await DB.init(dsn=DSN)
        mockpg.assert_called_with(dsn=DSN)

    @mock.patch('src.db.asyncpg.create_pool', new_callable=mock.AsyncMock)
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



if __name__ == "__main__":
    unittest.main()
