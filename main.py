import os
from threading import Thread
from flask import Flask, jsonify
from iotclient import get_room_status
from poller import poller_task



app = Flask(__name__)


@app.route("/")
def index():
    return "OK"

if __name__ == '__main__':
    calendarId='arduino.cc_3931313135363730363336@resource.calendar.google.com'
    #calendarId='c_18826hct7bgeqjrmmgrshqk2vbmi2@resource.calendar.google.com'
    thread = Thread(target=poller_task, args=(app,calendarId))
    thread.start()
    #thread2 = Thread(target=poller_task, args=(app,))
    #thread2.start()    
    
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
