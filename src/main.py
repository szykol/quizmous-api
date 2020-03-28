#! /usr/local/bin/python3

from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS, cross_origin
import jwt

app = Sanic()
CORS(app)

@app.route("/", methods=['GET', 'OPTIONS'])
async def test(request):
    return json(body={"name": "quizmous_api", "version": "0.0.1"}, status=200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
