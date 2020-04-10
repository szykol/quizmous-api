#! /usr/local/bin/python3

from quizmous_api.server import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
