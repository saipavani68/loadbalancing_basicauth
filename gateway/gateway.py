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
from flask import jsonify
import logging
from flask_basicauth import BasicAuth
from app import authenticateUser
from functools import wraps


app = flask.Flask(__name__)

basic_auth = BasicAuth(app)

app.config.from_envvar('APP_CONFIG')
users = app.config['USERS']
userNodesList = users['nodes']
userNodes = itertools.cycle(userNodesList)
userApiResources = users['endpoints']
timelines = app.config['TIMELINES']
timelinesNodesList = timelines['nodes']
timelinesNodes = itertools.cycle(timelinesNodesList)
timelinesApiResources = timelines['endpoints']

def check_credentials(username, password):
    response = authenticateUser(username, password)
    app.logger.info(response)
    return response.get_json()

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
    
    app.logger.info(flask.request.full_path)
    if flask.request.full_path in userApiResources:
        curr_node = next(userNodes)
    else:
        curr_node = next(timelinesNodes)
    # Each time you can see the log that the curr_node is changed from the list of nodes
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
        if curr_node in userNodesList:
            userNodesList.remove(curr_node)
        else:
            timelinesNodesList.remove(curr_node)
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
