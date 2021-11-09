import os

from .web import app

if __name__ == '__main__':
    app.run(port=8888, debug=True, threaded=True)
