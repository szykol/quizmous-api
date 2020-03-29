from unittest import TestCase
from src.response import Responses, create_response
from sanic import response
from ddt import ddt, data, unpack

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
