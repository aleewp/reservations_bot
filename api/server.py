import os
import json
from flask import Flask, request, Response

from api.base import json_response 
from resy.api import ResyWrapper

APP = Flask(__name__)


@APP.route('/find_table', methods=['GET'])
def find_table():
    request.get_data()
    kwargs = json.loads(request)
    wrapper = ResyWrapper
    required_params = ['reservation_date', 'num_people', 'venue_id']
    missing_params = [param for param in required_params not in kwargs]
    if len(missing_params) > 0:
        status, resp = 400, {'Error': f'Failed to make request due to missing {",".join(missing_params)}'}
    else:
        tables = wrapper.find_table(**kwargs)
        status, resp = 200, {'Results': tables}
    return json_response(status, resp)


@APP.route('/make_reservation', methods=['POST'])
def make_reservations():
    request.get_data()
    kwargs = json.loads(request)
    wrapper = ResyWrapper
    required_params = ['reservation_date', 'num_people', 'config_id']
    missing_params = [param for param in required_params not in kwargs]
    if len(missing_params) > 0:
        status, resp = 400, {'Error': f'Failed to make request due to missing {",".join(missing_params)}'}
    else:
        successful = wrapper.make_reservation(**kwargs)
        status, resp = 200, {'Results': successful}
    return json_response(status, resp)
