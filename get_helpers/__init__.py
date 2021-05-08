import logging
import geopy
from geopy import distance
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
    
    if req.params.get('device_id') is not None:
        device_id=req.params.get('device_id')
        helpers = help_giver.find({"device_id":device_id})
        all_helpers=[]
        for helper in helpers:
            all_helpers.append(helper)
        client.close()
        return func.HttpResponse(
            jsonify(all_helpers),
            status_code=200
        )
    else:
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
        
        pt = geopy.Point(latitude=lat, longitude=long)
        d = geopy.distance.distance(kilometers=distance)

        max_lat = float(d.destination(point=pt, bearing=0).format_decimal().split(",")[0])
        min_lat = float(d.destination(point=pt, bearing=180).format_decimal().split(",")[0])
        max_lon = float(d.destination(point=pt, bearing=90).format_decimal().split(",")[1])
        min_lon = float(d.destination(point=pt, bearing=270).format_decimal().split(",")[1])
        
        all_helpers = help_giver.find().sort("date_time", -1)
        helpers = []
        for helper in all_helpers:
            helper_lat = float(helper["helper_location"]["lattitude"])
            helper_lon = float(helper["helper_location"]["longitude"])
            if min_lat <= helper_lat <= max_lat and min_lon <= helper_lon <= max_lon:
                helpers.append(helper)
        client.close()
        return func.HttpResponse(
            jsonify(helpers),
            status_code=200
        )
