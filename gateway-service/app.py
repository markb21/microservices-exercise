from flask import *
import requests

app = Flask(__name__)

ADDRESS = 'localhost'
USER_SERVICE = ADDRESS+':3000'
MESSAGE_SERVICE = ADDRESS+':4000'


def authorize_request():
    if len(set(['client', 'uid', 'access-token']).intersection(set([item.lower() for item in request.headers.keys()]))) < 3:
        raise ValueError('Authentication data were not provided')

    response = requests.request('GET', USER_SERVICE + '/user/validate_token', headers={'client': request.headers['client'],
                                                                                    'uid': request.headers['uid'],
                                                                                    'access-token': request.headers['access-token']})
    if response.status_code >= 400 and response.status_code < 500:
        raise RuntimeError(response.text)

    return True


@app.route('/user',  methods=['POST'])
def create_user():
    if request.get_json() is None or ('email' and 'password') not in request.get_json().keys():
        raise ValueError('Missing data')

    if ('email' or 'password') not in request.get_json().keys():
        raise ValueError('User object does not contain crucial user data')
    user = dict()
    user['email'] = request.get_json()['email']
    user['password'] = request.get_json()['password']

    response = requests.request('POST', USER_SERVICE + '/user', headers=request.headers, json=user)
    return (response.text, response.status_code, response.headers.items())

@app.route('/user',  methods=['DELETE'])
def remove_user():
    authorize_request()

    response = requests.request('DELETE', USER_SERVICE + '/user', headers={'client': request.headers['client'],
                                                                                    'uid': request.headers['uid'],
                                                                                    'access-token': request.headers['access-token']})
    return (response.text, response.status_code, response.headers.items())


@app.route('/sign_in',  methods=['POST'])
def sign_in():
    if request.get_json() is None or ('email' and 'password') not in request.get_json().keys():
        raise ValueError('Missing data')

    if ('email' or 'password') not in request.get_json().keys():
        raise ValueError('User object does not contain required user data')
    user = dict()
    user['email'] = request.get_json()['email']
    user['password'] = request.get_json()['password']

    response = requests.request('POST', USER_SERVICE + '/user/sign_in', headers=request.headers, json=user)
    return (response.text, response.status_code, response.headers.items())


@app.route('/sign_out',  methods=['DELETE'])
def sign_out():
    authorize_request()

    response = requests.request('DELETE', USER_SERVICE + '/user/sign_out', headers={'client': request.headers['client'],
                                                                                    'uid': request.headers['uid'],
                                                                                    'access-token': request.headers['access-token']})
    return (response.text, response.status_code, response.headers.items())


@app.route('/message',  methods=['POST'])
def create_message():
    authorize_request()
    if request.get_json() is None or 'message' not in request.get_json().keys():
        raise ValueError('Missing data')

    request_body = dict()
    request_body['message'] = request.get_json()['message']

    response = requests.request('POST', MESSAGE_SERVICE + '/message', headers={'client': request.headers['client'],
                                                                                    'uid': request.headers['uid'],
                                                                                    'access-token': request.headers['access-token']},
                                json=request_body)
    return (response.text, response.status_code, response.headers.items())


@app.route('/messages',  methods=['GET'])
def get_messages():
    authorize_request()

    response = requests.request('GET', MESSAGE_SERVICE + '/messages', headers={'client': request.headers['client'],
                                                                                    'uid': request.headers['uid'],
                                                                                    'access-token': request.headers['access-token']})
    return (response.text, response.status_code, response.headers.items())


@app.route('/message',  methods=['DELETE'])
def delete_message():
    authorize_request()
    if 'message-id' not in [item.lower() for item in request.headers.keys()]:
        raise ValueError("Message ID is missing")

    response = requests.request('DELETE', MESSAGE_SERVICE + '/message', headers={'client': request.headers['client'],
                                                                                    'uid': request.headers['uid'],
                                                                                    'access-token': request.headers['access-token'],
                                                                                 'message-id': request.headers['message-id']})
    return (response.text, response.status_code, response.headers.items())


@app.errorhandler(ValueError)
def handle_invalid_usage(error):
    response = jsonify({'message': error.message})
    response.status_code = 400
    return response

@app.errorhandler(RuntimeError)
def handle_invalid_usage(error):
    response = jsonify({'message': error.message})
    response.status_code = 401
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='2000')
