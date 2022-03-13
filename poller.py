from datetime import datetime,timezone,timedelta
import threading
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from time import sleep
from RoomStatus import RoomStatus
import iotclient
import os
 
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']



def poller_task(app,calendar_id,room_name):
    with app.app_context():
        print("TNAME="+threading.currentThread().getName()+";INITIALIZE")
        roomstatus_iot = iotclient.get_room_status(room_name)
        print(roomstatus_iot)

        while True:
            print("TNAME="+threading.currentThread().getName()+";time="+str(datetime.utcnow()))
    
            roomstatus_gcal = get_calendar_status(calendar_id,room_name)
            print(roomstatus_gcal)
        
            if roomstatus_gcal != roomstatus_iot:
                #need to update roomstatus in iot
                #iotclient.update_room_status(roomstatus_gcal,roomstatus_iot)
                roomstatus_iot=iotclient.get_room_status(room_name)

            print("Going to sleep...")
            sleep(5)





def set_nextev_dates(startd,endd,tomorrow,result):
    if (startd<tomorrow):
        result.nextevstart = datetime.strftime(startd,"%H:%M")
        result.nextevend = datetime.strftime(endd,"%H:%M")
    else: 
        result.nextevstart = datetime.strftime(startd,"%Y-%m-%d %H:%M")
        result.nextevend = datetime.strftime(endd,"%H:%M")
    result.nextevtm=result.nextevstart+"-"+result.nextevend


def get_calendar_status(calendarId,room_name):
    result = RoomStatus()
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time    
    try:
        creds = service_account.Credentials.from_service_account_file(
            "credentials.json", scopes=SCOPES)
    
        service = build('calendar', 'v3', credentials=creds)

        #calendar = service.calendars().get(calendarId=calendarId).execute()
        #print(calendar)
    
        print('Getting the upcoming events')
        events_result = service.events().list(
                calendarId=calendarId,  \
                timeMin=now,  \
                maxResults=2, singleEvents=True,   \
                orderBy='startTime').execute()
        
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return result

        # Fetches the firts 2 events
        result.name=room_name
        evno = 1
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            summary = "unknown"
            if "summary" in event:
                    summary = event["summary"]

            startd=datetime.strptime(start,"%Y-%m-%dT%H:%M:%S%z")
            endd=datetime.strptime(end,"%Y-%m-%dT%H:%M:%S%z")

            tomorrow = datetime.now(timezone.utc) \
                        .replace(hour=0, minute=0, second=0, microsecond=0) \
                        + timedelta(days=1)

            if evno==1:
                #first event will tell if room is busy
                #if started before now, event is current
                if (startd<datetime.now(timezone.utc)):
                    result.busynow = RoomStatus.BUSY
                    result.curevmsg = summary
                    result.curevend = datetime.strftime(endd,"%H:%M")
                    result.curevstart = datetime.strftime(startd,"%H:%M")
                    result.curevtm = result.curevstart+"-"+result.curevend
                else:
                    #didn't start before now. will it start today ? 
                    #if starts today, calculate free until time
                    result.busynow = RoomStatus.FREE
                    if (startd<tomorrow):
                        result.curevmsg = "Free until "+datetime.strftime(startd,"%H:%M")
                    else: 
                        #else is free all day
                        result.curevmsg = "Free all day"
                            
                    #sets next events details
                    set_nextev_dates(startd,endd,tomorrow,result)
                    result.nextevmsg = summary
                    
            if evno==2:
                #second event is useful only if room is busy to set next mtg details
                if result.busynow==RoomStatus.BUSY:
                    result.nextevmsg = summary
                    set_nextev_dates(startd,endd,tomorrow,result)
                    
            evno = evno+1

    except RuntimeError as error:
        print('An error occurred: %s' % error)
    
    return result
