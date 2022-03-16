
from datetime import datetime,timezone,timedelta
from socket import timeout
import threading
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from time import sleep
from RoomStatus import RoomStatus
from iotclient import IotClient
import os
import socket    
import time
 
SCOPES = ['https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events']



def poller_task(app,calendar_id,room_name,client_id,client_secret):
    with app.app_context():
        print("TNAME="+threading.currentThread().getName()+";INITIALIZE")
        socket.setdefaulttimeout(5)
        
        #at start, get current status from iotcloud
        updatestatusfromiot=True
        iotc=IotClient(client_id,client_secret)

        while True:
            print("TNAME="+threading.currentThread().getName()+";time="+str(datetime.utcnow()))
    
            if (updatestatusfromiot):
                roomstatus_iot = RoomStatus()
                attempts = 1
                while(roomstatus_iot.is_valid()==False and attempts<3):
                    roomstatus_iot = iotc.get_room_status(room_name)
                    print(roomstatus_iot)
                    sleep(2)
                    attempts=attempts+1
                #cache status until next update is needed
                updatestatusfromiot=False  

            #now get status from google calendar 
            attempts = 1
            roomstatus_gcal = RoomStatus()
            while(roomstatus_gcal.is_valid()==False and attempts<3):
                roomstatus_gcal = get_calendar_status(calendar_id,room_name)
                print(roomstatus_gcal)
                sleep(2)
                attempts=attempts+1
        
            if roomstatus_gcal.is_valid() and roomstatus_iot.is_valid() and roomstatus_gcal != roomstatus_iot:
                #need to update roomstatus in iot
                print("Updating Room status in IoTCloud...")
                iotc.update_room_status(roomstatus_gcal,roomstatus_iot)
                #next time, force update from iotcloud to check that update was performed
                updatestatusfromiot=True 
            elif roomstatus_iot.is_valid()==False:
                #if retrieval of status didn't go well, try again next time
                updatestatusfromiot=False
                
            print("Going to sleep...")
            sleep(5)





def set_nextev_dates(startd,endd,tomorrow,result):
    #utility to set next events dates in right format
    #if it's within the day use only H:M otherwise put day in front
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
    
        print('Getting the upcoming events')
        events_result = service.events().list(
                calendarId=calendarId,  \
                timeMin=now,  \
                maxResults=2, singleEvents=True,   \
                orderBy='startTime').execute()
        
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            result.valid = False 
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

        result.valid = True 
    except (RuntimeError,TimeoutError,socket.timeout) as error:
        result.valid = False 
        print('An error occurred: %s' % error)
    
    return result



def insert_instantmeeting(calendarId,room_name,duration_mins):
    #https://developers.google.com/calendar/api/v3/reference/events/insert#examples
    startdt = datetime.utcnow()
    mins = startdt.minute
    #round minutes to 00,15,30,45
    mins = mins - (mins % 15)
    startdt = startdt.replace(minute=mins, second=0, microsecond=0)
    #round duration to multiples of 15mins
    duration_mins = int(duration_mins / 15)*15
    enddt = startdt+timedelta(minutes=duration_mins)
    startstr = datetime.strftime(startdt,"%Y-%m-%dT%H:%M:%S+0000")   
    endstr = datetime.strftime(enddt,"%Y-%m-%dT%H:%M:%S+0000")   

    try:
        creds = service_account.Credentials.from_service_account_file(
            "credentials.json", scopes=SCOPES)
        creds = creds.with_subject("tablettini@arduino.cc")
    
        service = build('calendar', 'v3', credentials=creds)
    
        print('Inserting instant meeting')
        meetid = "im_"+startstr
        event = {
            'summary': 'Meeting',
            'description': meetid,
            'start': {
                'dateTime': startstr,
                'timeZone': "UTC"
            },
            'end': {
                'dateTime': endstr,
                'timeZone': "UTC"
            }
            }
        print(event)
        event = service.events().insert(calendarId=calendarId, body=event).execute() 
        return True

    except (RuntimeError,TimeoutError,socket.timeout,HttpError) as error:
        print('An error occurred: %s' % error)
        return False