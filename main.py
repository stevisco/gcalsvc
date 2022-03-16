import os
from threading import Thread
from flask import Flask, abort, jsonify, request
from RoomStatus import RoomStatus
from poller import get_calendar_status, poller_task,insert_instantmeeting
from datetime import datetime,timezone,timedelta 
import time 

app = Flask(__name__)


@app.route("/")
def index():
    return "OK"


@app.route("/newmeeting",methods=['POST'])
def newmeeting():
    content = request.get_json(True)
    calendar_id = content.get("calendar_id","")
    room_name = content.get("room_name","")
    client_secret = content.get("client_secret","")
    client_id = content.get("client_id","")
    duration_str = content.get("duration_mins","60")
    if calendar_id=="" or room_name=="" or client_secret=="" or client_id=="":
        abort(400,"Required parameters in request body are missing")
    #calendar_id='arduino.cc_3931313135363730363336@resource.calendar.google.com'
    #room_name="blue_room"
    #client_secret="***REMOVED***"
    #client_id="SOeu9scvEKBMrRjG8olnDAwegufvTiCp"

    duration_mins = int(duration_str)
    roomstatus = get_calendar_status(calendar_id,room_name)
    if (roomstatus.busynow==RoomStatus.BUSY):
        abort(400,"Could not insert new meeting, room already busy")

    insertedok = insert_instantmeeting(calendar_id,room_name,duration_mins)
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
    
    #thread = Thread(target=poller_task, args=(app,calendar_id,room_name,client_id,client_secret))
    #thread.start()
    #thread2 = Thread(target=poller_task, args=(app,))
    #thread2.start()    
    
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
