
from datetime import datetime
from gcalclient import GCalClient
from socket import timeout
import threading
from time import sleep
from roomstatus import RoomStatus
from iotclient import IotClient
import socket    
 


def poller_task(app,calendar_id,room_name,client_id,client_secret):
    with app.app_context():
        print("TNAME="+threading.currentThread().getName()+";INITIALIZE")
        socket.setdefaulttimeout(5)
        iotc=IotClient(client_id,client_secret)
        gcalc=GCalClient(calendar_id,room_name)

        #at start, get current status from iotcloud
        updatestatusfromiot=True

        while True:
            print("POLL;"+threading.currentThread().getName()+";time="+str(datetime.utcnow()))
    
            if (updatestatusfromiot):
                roomstatus_iot = RoomStatus()
                attempts = 1
                while(roomstatus_iot.is_valid()==False and attempts<3):
                    roomstatus_iot = iotc.get_room_status(room_name)
                    #print(roomstatus_iot)
                    sleep(1)
                    attempts=attempts+1
                #cache status until next update is needed
                updatestatusfromiot=False  

            #now get status from google calendar 
            attempts = 1
            roomstatus_gcal = RoomStatus()
            while(roomstatus_gcal.is_valid()==False and attempts<3):
                roomstatus_gcal = gcalc.get_calendar_status()
                #print(roomstatus_gcal)
                sleep(1)
                attempts=attempts+1
        
            if roomstatus_gcal.is_valid() and roomstatus_iot.is_valid() and roomstatus_gcal != roomstatus_iot:
                #need to update roomstatus in iot
                print("Updating Room status in IoTCloud...")
                iotc.update_room_status(roomstatus_gcal,roomstatus_iot)
                #next time, force update from iotcloud to check that update was performed
                updatestatusfromiot=True 
            elif roomstatus_iot.is_valid()==False:
                #if retrieval of status didn't go well, try again next time
                updatestatusfromiot=True
                
            sleep(3)





