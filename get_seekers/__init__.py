import logging

import json
from datetime import datetime
import os
import certifi
from bson.json_util import ObjectId
from pymongo import MongoClient

import azure.functions as func

DB_NAME = os.environ["DB_NAME"]
MONGO_CONNECTION = os.environ["MONGO_CONNECTION"]
help_seeker_collection = os.environ["help_seeker_collection"]

client = MongoClient(MONGO_CONNECTION, tlsCAFile=certifi.where())
db = client[DB_NAME]
help_seeker = db[help_seeker_collection]

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Trigered app for get_seekers')

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

    all_seekers = help_seeker.find()
    seekers = []
    for seeker in all_seekers:
        seeker_lat = float(seeker["seeker_location"]["lattitude"])
        seeker_lon = float(seeker["seeker_location"]["longitude"])
        if min_lat <= seeker_lat <= max_lat and min_lon <= seeker_lon <= max_lon:
            seekers.append(seeker)
    return func.HttpResponse(
        str(seekers),
        status_code=200
    )