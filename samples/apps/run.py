# -*- coding:utf-8 -*-

import logging
import os

from flask import Flask

from session_jp.session import session
from hyakucnt.session import hyakucnt
from todaykoh.session import todaykoh
from spacegeek_jp.spacegeek import spacegeek
from historybuff_jp.historybuff import historybuff

# 2018-12-26 Y.Kawada
# excute example:
#  python run.py or
#  gunicorn-3.6 -w 6 run:app -b localhost:3000

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

app.register_blueprint(session)
app.register_blueprint(hyakucnt)
app.register_blueprint(todaykoh)
app.register_blueprint(spacegeek)
app.register_blueprint(historybuff)

logging.getLogger('flask_app').setLevel(logging.DEBUG)


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True,port=3000,threaded=True)
