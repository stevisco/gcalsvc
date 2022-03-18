from threading import Thread
from poller import poller_task
import json

if __name__ == '__main__':

    #calendar_id='arduino.cc_3931313135363730363336@resource.calendar.google.com'
    #room_name="blue_room"
    #client_secret="***REMOVED***"
    #client_id="SOeu9scvEKBMrRjG8olnDAwegufvTiCp"

    with open('config.json', 'r') as f:
        config = json.load(f)
    
    client_secret=config.get("iot_client_secret","")
    client_id=config.get("iot_client_id","")
    insert_asuser=config.get("gcal_insert_asuser","")

    rooms = config.get("rooms",[])
    for room in rooms:
        calendar_id = room.get("gcal_calendarid","")
        room_name = room.get("room_name","")
        print("Starting thread for room = "+room_name)    
        thread = Thread(target=poller_task, args=(calendar_id,room_name,client_id,client_secret))
        thread.start()
    
    
