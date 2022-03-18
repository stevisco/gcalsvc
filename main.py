import os
import socket
from threading import Thread
from urllib.error import HTTPError
from flask import Flask, abort, request
from roomstatus import RoomStatus 
from iotclient import IotClient
from poller import poller_task
from oauthlib.oauth2 import MissingTokenError
from gcalclient import GCalClient

app = Flask(__name__)


@app.route("/")
def index():
    return "OK"


@app.route("/newmeeting",methods=['POST'])
def newmeeting():
    
    content = request.get_json(True)
    room_name = content.get("room_name","")
    client_secret = content.get("client_secret","")
    client_id = content.get("client_id","")
    duration_str = content.get("duration_mins","60")
    if room_name=="" or client_secret=="" or client_id=="":
        abort(400,"Required parameters in request body are missing")
    
    #TODO: retrieve this from config
    calendar_id='arduino.cc_3931313135363730363336@resource.calendar.google.com'
    
    gcalc = GCalClient(calendar_id,room_name)

    try:
        #use iotcloudclient only to execute oauth
        iotc = IotClient(client_id,client_secret)
        iotc.get_token()
    except (RuntimeError,TimeoutError,socket.timeout,HTTPError,MissingTokenError) as error:
            print('An error occurred: %s' % error)
            abort(401,"ERROR - invalid authentication")

    duration_mins = int(duration_str)
    roomstatus = gcalc.get_calendar_status()
    if (roomstatus.busynow==RoomStatus.BUSY):
        abort(400,"Could not insert new meeting, room already busy")

    insertedok = gcalc.insert_instantmeeting(duration_mins)
    if insertedok: 
        return "Meeting inserted"
    else: 
        abort(500,"ERROR - could not insert meeting")

    



if __name__ == '__main__':
    calendar_id='arduino.cc_3931313135363730363336@resource.calendar.google.com'
    room_name="blue_room"
    client_secret="***REMOVED***"
    client_id="SOeu9scvEKBMrRjG8olnDAwegufvTiCp"

    #calendar_id='c_18826hct7bgeqjrmmgrshqk2vbmi2@resource.calendar.google.com'
    
    thread = Thread(target=poller_task, args=(app,calendar_id,room_name,client_id,client_secret))
    thread.start()
    #thread2 = Thread(target=poller_task, args=(app,))
    #thread2.start()    
    
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
