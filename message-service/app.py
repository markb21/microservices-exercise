from flask import *
import pymongo
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import json
import os

app = Flask(__name__)

client = MongoClient(
    '192.168.0.129',
    27017)
db = client.twitter


@app.route('/message',  methods=['POST'])
def create_message():
    if request.get_json() is None or 'message' not in request.get_json().keys():
        raise ValueError('Missing message')

    message = dict()
    message['text'] = request.get_json()['message']
    message['uid'] = request.headers['uid']
    message['time_stamp'] = datetime.now()
    print message
    try:
        db.messages.insert_one(message)
    except Exception:
        raise ValueError('Problem writing message into database')

    response = jsonify({'message': 'success'})
    response.status_code = 200
    return response


@app.route('/message',  methods=['DELETE'])
def delete_message():
    if 'message-id' not in [key.lower() for key in request.headers.keys()]:
        raise ValueError('Missing message id')

    try:
        message = dict()
        message['_id'] = ObjectId(request.headers['message-id'])
    except Exception:
        raise ValueError('Problem while retrieving message id')

    try:
        result = db.messages.delete_one(message)
    except Exception:
        raise ValueError("Could not connect to the database")

    # try:
    #     if result['deleted_count'] > 0:
    #         response = jsonify({'message': 'Message deleted.'})
    #         response.status_code = 200
    #     else:
    #         response = jsonify({'message': 'Nothing was deleted.'})
    #         response.status_code = 200
    # except Exception:
    #     raise ValueError("Problems with reading the response")

    response = jsonify({'message': 'Message deleted.'})
    response.status_code = 200

    return response

@app.route('/messages',  methods=['GET'])
def get_messages():
    # add connection to Subscription Service
    uids = [request.headers['uid']]
    messages = list()

    for message in db.messages.find({"uid": {"$in": uids}}).sort("time_stamp", pymongo.DESCENDING):
        message["_id"] = str(message["_id"])
        message["time_stamps"] = str(message["time_stamp"])
        messages.append(message)

    response = jsonify({'messages': messages})
    response.status_code = 200
    return response

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
    app.run(host='0.0.0.0', port='4000')
