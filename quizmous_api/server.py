
from sanic_cors import CORS, cross_origin
from .db import DB, select_model_from_db, insert_model_to_db
from .version import get_api_version
from .common import jwt, extract_jwt

from quizmous_api import app, DSN, VERSION, SERIAL, Quiz
from quizmous_api.api.endpoints import init_endpoints
import asyncio

async def main():
    """Main program
    """
    await DB.init(dsn=DSN)
    server = app.create_server(host="0.0.0.0", port=8000, return_asyncio_server=True)
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(server, loop=loop)

    return task        

def run():
    """Runs main using asyncio
    """
    server = asyncio.ensure_future(main())
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt as e:
        asyncio.get_event_loop().stop()