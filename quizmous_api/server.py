from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS, cross_origin
from .db import DB, select_model_from_db, insert_model_to_db
from .version import get_api_version
from .common import jwt, extract_jwt

from quizmous_api import app, DSN, VERSION, SERIAL, Quiz
import asyncio

@app.route("/", methods=['GET', 'OPTIONS'])
async def test(request):
    body = {"name": "quizmous_api"}
    body.update(VERSION)
    return json(body=body, status=200)

@app.route("/quiz", methods=['GET', 'OPTIONS'])
async def get_quiz(request):
    quizes = await select_model_from_db(Quiz)

    return json(body=[q.to_dict() for q in quizes], status=200)

@app.route("/quiz", methods=['POST'])
async def add_quiz(request):
    ok, payload = extract_jwt(request.body, SERIAL)
    quiz = Quiz.from_dict(payload)
    await insert_model_to_db(quiz)

    return json(body={"message": "success"}, status=201)

async def main():
    await DB.init(dsn=DSN)
    server = app.create_server(host="0.0.0.0", port=8000, return_asyncio_server=True)
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(server, loop=loop)

    return task        

def run():
    server = asyncio.ensure_future(main())
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt as e:
        asyncio.get_event_loop().stop()