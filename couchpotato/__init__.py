from couchpotato.core.auth import requires_auth
from couchpotato.core.event import fireEvent
from couchpotato.core.logger import CPLog
from couchpotato.environment import Env
from flask.app import Flask
from flask.globals import request
from flask.helpers import url_for
from flask.module import Module
from flask.templating import render_template
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker
from werkzeug.utils import redirect
import os

log = CPLog(__name__)

app = Flask(__name__)
web = Module(__name__, 'web')


def get_session(engine = None):
    engine = engine if engine else get_engine()
    return scoped_session(sessionmaker(bind = engine))

def get_engine():
    return create_engine(Env.get('db_path'), echo = False)


""" Web view """
@web.route('/')
@requires_auth
def index():
    return render_template('index.html', sep = os.sep, fireEvent = fireEvent)

@app.errorhandler(404)
def page_not_found(error):
    index_url = url_for('web.index')
    url = getattr(request, 'path')[len(index_url):]
    return redirect(index_url + '#' + url)

