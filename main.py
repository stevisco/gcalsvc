import os
import socket
from threading import Thread
from urllib.error import HTTPError
from flask import Flask, abort, jsonify, request
from numpy import insert
from roomstatus import RoomStatus 
from iotclient import IotClient
from poller import poller_task
from oauthlib.oauth2 import MissingTokenError
from gcalclient import GCalClient
import json
import mylogger

app = Flask(__name__)

logger = mylogger.getlogger(__name__)


@app.route("/")
def index():
    return "OK"


@app.route("/meetings",methods=['GET'])
def list_meetings():
    logger.info("Started executing getmeetings")
    #read auth data from args
    client_id = request.args.get("client_id","")
    room_name=request.args.get("room_name","")
    authh = request.headers.get("Authorization","Bearer ")
    client_secret = authh[7:len(authh)]
    if room_name=="" or client_secret=="" or client_id=="":
        abort(400,"Required parameters in request body are missing")
    
    #retrieve config
    with open('config.json', 'r') as f:
        config = json.load(f)
    rooms=config.get("rooms",[])
    calendar_id = ""
    for room in rooms:
        if room.get("room_name","")==room_name:
            calendar_id=room.get("gcal_calendar_id","")

    if calendar_id=="":
        abort(400,"Required parameter not matching configuration for room_name="+room_name)

    gcalc = GCalClient(calendar_id,room_name)

    try:
        #use iotcloudclient only to execute oauth
        iotc = IotClient(client_id,client_secret)
        iotc.get_token()
    except (RuntimeError,TimeoutError,socket.timeout,HTTPError,MissingTokenError) as error:
            logger.error('An error occurred: %s' % error)
            abort(401,"ERROR - invalid authentication")

    roomstatus = gcalc.get_calendar_status()
    return roomstatus.toJSON()




@app.route("/meetings",methods=['POST'])
def newmeeting():
    content = request.get_json(True)
    #read auth data from request
    client_secret = content.get("client_secret","")
    client_id = content.get("client_id","")
    duration_str = content.get("duration_mins","60")
    room_name = content.get("room_name","")

    if room_name=="" or client_secret=="" or client_id=="":
        abort(400,"Required parameters in request body are missing")
    
    #retrieve config
    with open('config.json', 'r') as f:
        config = json.load(f)
    rooms=config.get("rooms",[])
    insert_asuser=config.get("gcal_insert_asuser","")
    calendar_id = ""
    for room in rooms:
        if room.get("room_name","")==room_name:
            calendar_id=room.get("gcal_calendar_id","")

    if calendar_id=="":
        abort(400,"Required parameter not matching configuration for room_name="+room_name)

    #calendar_id='arduino.cc_3931313135363730363336@resource.calendar.google.com'
    #insert_asuser="tablettini@arduino.cc"
    
    gcalc = GCalClient(calendar_id,room_name)

    try:
        #use iotcloudclient only to execute oauth
        iotc = IotClient(client_id,client_secret)
        iotc.get_token()
    except (RuntimeError,TimeoutError,socket.timeout,HTTPError,MissingTokenError) as error:
            logger.error('An error occurred: %s' % error)
            abort(401,"ERROR - invalid authentication")

    duration_mins = int(duration_str)
    roomstatus = gcalc.get_calendar_status()
    if (roomstatus.busynow==RoomStatus.BUSY):
        abort(400,"Could not insert new meeting, room already busy")

    attempts=1
    insertedok=False
    while insertedok==False and attempts<3:
        insertedok = gcalc.insert_instantmeeting(duration_mins,insert_asuser)
        attempts = attempts+1

    if insertedok: 
        logger.info("Meeting created")
        return "Meeting created",201
    else: 
        logger.error("Could not insert meeting")
        abort(500,"ERROR - could not insert meeting")

    

    



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
