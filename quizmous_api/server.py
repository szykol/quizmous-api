from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS, cross_origin
from .db import DB
from .version import get_api_version
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

@app.route("/db_test", methods=['GET', 'OPTIONS'])
async def db_test(request):
    await DB.init(dsn=DSN)
    await DB.get_pool().execute(""" INSERT INTO dummy_tbl (name) VALUES ($1) """, "quizmous_api")
    questions = await DB.get_pool().fetch(""" SELECT * FROM quiz_question WHERE quiz_id=$1""", 1)
    questions = [dict(q) for q in questions]
    return json(body={"questions": questions}, status=200)
