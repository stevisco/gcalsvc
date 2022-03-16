import os
from threading import Thread
from flask import Flask, abort, jsonify
from poller import poller_task,insert_instantmeeting
from datetime import datetime,timezone,timedelta 
import time 

app = Flask(__name__)


@app.route("/")
def index():
    return "OK"


@app.route("/newmeeting")
def newmeeting():
    calendar_id='arduino.cc_3931313135363730363336@resource.calendar.google.com'
    room_name="blue_room"
    client_secret="***REMOVED***"
    client_id="SOeu9scvEKBMrRjG8olnDAwegufvTiCp"

    duration_mins = 30
    code = insert_instantmeeting(calendar_id,room_name,duration_mins)
    if code: 
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
