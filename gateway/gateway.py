#
# Simple API gateway in Python
#
# Inspired by <https://github.com/vishnuvardhan-kumar/loadbalancer.py>
#
#   $ python3 -m pip install Flask python-dotenv
#

import sys
import flask, itertools
from flask import request
import requests
import logging
from flask_basicauth import BasicAuth
from functools import wraps


app = flask.Flask(__name__)

basic_auth = BasicAuth(app)

app.config.from_envvar('APP_CONFIG')
nodesList = app.config['NODES']
nodes = itertools.cycle(nodesList)

def check_credentials(username, password):
    app.logger.info(username)

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return flask.Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_basic_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_credentials(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.errorhandler(404)
@requires_basic_auth
def route_page(err):
    # Each time you can see the log that the curr_node is changed from the list of nodes
    curr_node = next(nodes)
    app.logger.info(curr_node)
    try:
        response = requests.request(
            flask.request.method,
            curr_node + flask.request.full_path,
            data=flask.request.get_data(),
            headers=flask.request.headers,
            cookies=flask.request.cookies,
            stream=True,
        )
    except requests.exceptions.RequestException as e:
        #removing node or server in case of connection refused error or HTTP status code in the 500 range
        if curr_node in nodesList:
            nodesList.remove(curr_node)
        return flask.json.jsonify({
            'method': e.request.method,
            'url': e.request.url,
            'exception': type(e).__name__,
        }), 503

    headers = remove_item(
        response.headers,
        'Transfer-Encoding',
        'chunked'
    )

    return flask.Response(
        response=response.content,
        status=response.status_code,
        headers=headers,
        direct_passthrough=True,
    )


def remove_item(d, k, v):
    if k in d:
        if d[k].casefold() == v.casefold():
            del d[k]
    return dict(d)
