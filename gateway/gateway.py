#
# Simple API gateway in Python
#
# Inspired by <https://github.com/vishnuvardhan-kumar/loadbalancer.py>
#
#   $ python3 -m pip install Flask python-dotenv
#

import sys

import flask, itertools
import requests
import logging

app = flask.Flask(__name__)
app.config.from_envvar('APP_CONFIG')
nodesList = app.config['NODES']
nodes = itertools.cycle(nodesList)

@app.errorhandler(404)
def route_page(err):
    # Each time you can see the log that the curr_node is changed from the list of nodes
    curr_node = next(nodes)
    app.logger.info(curr_node)
    try:
        response = requests.request(
            flask.request.method,
            curr_node + '/',
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
