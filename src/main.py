#! /usr/local/bin/python3

from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS, cross_origin
from db import DB
import jwt

app = Sanic()
CORS(app)
DBNAME = app.config['DBNAME'] if "DBNAME" in app.config else 'quiz' 
DSN = 'postgres://api:foobar@postgres_api:5432/{}'.format(DBNAME)

@app.route("/", methods=['GET', 'OPTIONS'])
async def test(request):
    return json(body={"name": "quizmous_api", "version": "0.0.1"}, status=200)

@app.route("/db_test", methods=['GET', 'OPTIONS'])
async def db_test(request):
    await DB.init(dsn=DSN)
    await DB.get_pool().execute(""" INSERT INTO dummy_tbl (name) VALUES ($1) """, "quizmous_api")

    return json(body={"status": "ok"}, status=200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
