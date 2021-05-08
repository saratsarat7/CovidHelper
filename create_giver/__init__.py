import logging
import pytz
from datetime import datetime
import os
import certifi
from pymongo import MongoClient

import azure.functions as func

DB_NAME = os.environ["DB_NAME"]
MONGO_CONNECTION = os.environ["MONGO_CONNECTION"]
help_giver_collection = os.environ["help_giver_collection"]
tz_NY = pytz.timezone('Asia/Kolkata')

client = MongoClient(MONGO_CONNECTION, tlsCAFile=certifi.where())
db = client[DB_NAME]
help_giver = db[help_giver_collection]

create_helper_request_body = {
    "help_type": "",
    "helper_name": "",
    "helper_phone_number": "",
    "helper_location": {
        "longitude": "",
        "lattitude": ""
    },
    "helper_area": "",
    "device_id":""
}

def filter_body(expected_body, ui_body):
    request_body = {}
    for key in expected_body.keys():
        request_body[key] = ui_body[key]
    return request_body

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Trigered app for create_giver')

    get_parms = req.params
    if get_parms:
        return func.HttpResponse(
            "This endpoint is not accepting any GET requests",
            status_code=301
        )
    else:
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                "Incorrect value in request BODY.",
                status_code=302
            )
        try:
            request_body = filter_body(create_helper_request_body, req_body)
            request_body['helper_location']["longitude"] = round(request_body['helper_location']["longitude"], 6)
            request_body['helper_location']["lattitude"] = round(request_body['helper_location']["lattitude"], 6)
            datetime_NY = datetime.now(tz_NY)
            date_time=datetime_NY.strftime("%Y-%m-%d %H:%M:%S")
            request_body['date_time'] = date_time
            object_ID = help_giver.insert_one(request_body).inserted_id
            return func.HttpResponse(
                f"Success {object_ID}",
                status_code=200
            )
        except Exception as e:
            logging.info(e)
            return func.HttpResponse(
                "Unknown error in processing the request.",
                status_code=303
            )
