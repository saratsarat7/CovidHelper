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
help_seeker_collection = os.environ["help_seeker_collection"]

client = MongoClient(MONGO_CONNECTION, tlsCAFile=certifi.where())
db = client[DB_NAME]
help_seeker = db[help_seeker_collection]

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
    logging.info('Trigered app for get_seekers')
    
    if req.params.get('device_id') is not None:
        device_id=req.params.get('device_id')
        seekers = help_seeker.find({"device_id":device_id})
        all_seekers=[]
        for seeker in seekers:
            all_seekers.append(seeker)
        client.close()
        return func.HttpResponse(
            jsonify(all_seekers),
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

        all_seekers = help_seeker.find().sort("date_time", -1)
        seekers = []
        for seeker in all_seekers:
            seeker_lat = float(seeker["seeker_location"]["lattitude"])
            seeker_lon = float(seeker["seeker_location"]["longitude"])
            if min_lat <= seeker_lat <= max_lat and min_lon <= seeker_lon <= max_lon:
                seekers.append(seeker)
        client.close()
        return func.HttpResponse(
            jsonify(seekers),
            status_code=200
        )
