from flask import Flask

import json
from datetime import datetime

import certifi
from bson.json_util import ObjectId
from flask import Flask, request, jsonify
from pymongo import MongoClient

from resources.config import *
from resources.request_bodies import *

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.__str__()
        return super(MyEncoder, self).default(obj)

app = Flask(__name__)
# app.config["DEBUG"] = True
app.json_encoder = MyEncoder
client = MongoClient(MONGO_CONNECTION, tlsCAFile=certifi.where())
db = client[DB_NAME]
help_seeker = db[help_seeker_collection]
help_giver = db[help_giver_collection]

@app.route('/get_seekers', methods=['GET'])
def get_seeker_requests():
    query_parameters = request.args
    long = float(query_parameters.get('long'))
    lat = float(query_parameters.get('lat'))
    distance = int(query_parameters.get('dist'))

    la = 0.004963
    lo = 0.003965
    max_lat = round(lat + (la * distance), 6)
    min_lat = round(lat - (la * distance), 6)
    max_lon = round(long + (lo * distance), 6)
    min_lon = round(long - (lo * distance), 6)

    all_seekers = help_seeker.find()
    seekers = []
    for seeker in all_seekers:
        seeker_lat = seeker["seeker_location"]["lattitude"]
        seeker_lon = seeker["seeker_location"]["longitude"]
        if min_lat <= seeker_lat <= max_lat and min_lon <= seeker_lon <= max_lon:
            seekers.append(seeker)
    return jsonify(seekers)


@app.route('/get_helpers', methods=['GET'])
def get_helper_requests():
    query_parameters = request.args
    long = float(query_parameters.get('long'))
    lat = float(query_parameters.get('lat'))
    distance = int(query_parameters.get('dist'))

    la = 0.004963
    lo = 0.003965
    max_lat = round(lat + (la * distance), 6)
    min_lat = round(lat - (la * distance), 6)
    max_lon = round(long + (lo * distance), 6)
    min_lon = round(long - (lo * distance), 6)

    all_helpers = help_giver.find()
    helpers = []
    for helper in all_helpers:
        helper_lat = helper["helper_location"]["lattitude"]
        helper_lon = helper["helper_location"]["longitude"]
        if min_lat <= helper_lat <= max_lat and min_lon <= helper_lon <= max_lon:
            helpers.append(helper)
    return jsonify(helpers)


@app.route('/create_seeker', methods=['POST'])
def create_seeker_request():
    data = request.json
    request_body = filter_body(create_seeker_request_body, data)
    request_body['seeker_location']["longitude"] = round(request_body['seeker_location']["longitude"], 6)
    request_body['seeker_location']["lattitude"] = round(request_body['seeker_location']["lattitude"], 6)
    request_body['date_time'] = datetime.now()
    res = help_seeker.insert_one(request_body).inserted_id
    return jsonify(request_body)


@app.route('/create_giver', methods=['POST'])
def create_giver_request():
    data = request.json
    request_body = filter_body(create_helper_request_body, data)
    request_body['date_time'] = datetime.now()
    res = help_giver.insert_one(request_body).inserted_id
    return jsonify(request_body)


@app.route('/add_comment', methods=['PUT'])
def add_comment():
    # getting post id from params
    post_id = request.args.get("id")
    # getting comment from body
    comment = request.json
    comment["data_time"] = datetime.now()
    # finding post by id
    seeker = help_seeker.find_one({"_id": ObjectId(post_id)})
    # Adding comment
    all_comments = seeker['comment']
    all_comments.append(comment)
    # Updating the post with new comment
    res = help_seeker.update_one({"_id": ObjectId(post_id)}, {"$set": {"comment": all_comments}})
    return jsonify(seeker)


def filter_body(expected_body, ui_body):
    request_body = {}
    for key in expected_body.keys():
        request_body[key] = ui_body[key]
    return request_body


if __name__ == '__main__':
    app.run()
