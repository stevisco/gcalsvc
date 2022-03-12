import os
from threading import Thread
from flask import Flask, jsonify
from poller import poller_task



app = Flask(__name__)



@app.route("/")
def index():
    return "OK"

if __name__ == '__main__':
    thread = Thread(target=poller_task, args=(app,))
    #thread.daemon = True
    thread.start()
    
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
