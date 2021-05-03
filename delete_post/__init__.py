import logging

from bson.json_util import ObjectId
import os
import certifi
from pymongo import MongoClient

import azure.functions as func

DB_NAME = os.environ["DB_NAME"]
MONGO_CONNECTION = os.environ["MONGO_CONNECTION"]
help_seeker_collection = os.environ["help_seeker_collection"]
help_giver_collection = os.environ["help_giver_collection"]

client = MongoClient(MONGO_CONNECTION, tlsCAFile=certifi.where())
db = client[DB_NAME]
help_seeker = db[help_seeker_collection]
help_giver = db[help_giver_collection]

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Trigered app for delete_post')

    req_Id = req.params.get('id')
    
    if (not req_Id):
        return func.HttpResponse(
            "Invalid Request",
            status_code=301
        )

    req_helper = help_giver.find_one({"_id": ObjectId(req_Id)})
    req_seeker = help_seeker.find_one({"_id": ObjectId(req_Id)})

    if req_helper is not None:
        help_giver.remove({"_id": ObjectId(req_Id)})
    elif req_seeker is not None:
        help_seeker.remove({"_id": ObjectId(req_Id)})

    client.close()

    return func.HttpResponse(
        "Delete Successful",
        status_code=200
    )