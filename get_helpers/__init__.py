import logging

import datetime
from bson.json_util import ObjectId
import os
import certifi
from pymongo import MongoClient

import azure.functions as func

DB_NAME = os.environ["DB_NAME"]
MONGO_CONNECTION = os.environ["MONGO_CONNECTION"]
help_giver_collection = os.environ["help_giver_collection"]

client = MongoClient(MONGO_CONNECTION, tlsCAFile=certifi.where())
db = client[DB_NAME]
help_giver = db[help_giver_collection]

def jsonify(resp):
    response_list = []
    for r in resp:
        response = {}
        for key,value in r.items():
            if isinstance(value,ObjectId):
                response[key]=str(value)
            elif isinstance(value,datetime.datetime):
                response[key] = str(value)
            else:
                response[key]=value
        response_list.append(response)
    return str(response_list)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Trigered app for get_helpers')

    long = req.params.get('long')
    lat = req.params.get('lat')
    distance = req.params.get('dist')
    
    if (not long) or (not lat) or (not distance):
        return func.HttpResponse(
            "Resquest parms not complete send all query parms.",
            status_code=301
        )

    # Convert request value to float/int Type
    long = float(long)
    lat = float(lat)
    distance = int(distance)
    
    la = 0.004963
    lo = 0.003965
    max_lat = round(lat + (la * distance), 6)
    min_lat = round(lat - (la * distance), 6)
    max_lon = round(long + (lo * distance), 6)
    min_lon = round(long - (lo * distance), 6)

    all_helpers = help_giver.find()
    helpers = []
    for helper in all_helpers:
        helper_lat = float(helper["helper_location"]["lattitude"])
        helper_lon = float(helper["helper_location"]["longitude"])
        if min_lat <= helper_lat <= max_lat and min_lon <= helper_lon <= max_lon:
            helpers.append(helper)
    return func.HttpResponse(
        jsonify(helpers),
        status_code=200
    )