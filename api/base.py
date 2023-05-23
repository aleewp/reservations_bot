import json

from flask import request, abort, Response


def json_response(status, data):
    """
    Creates a Flask response from Python object, with the correct mimetype
    """
    return Response(json.dumps(data), status=status, mimetype='application/json')
