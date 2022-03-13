from datetime import datetime,timezone,timedelta
import threading
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from time import sleep
import iotclient
import os
 
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']



def poller_task(app,calendarId):
    with app.app_context():
        
        while True:
            result = {}
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
                
            print("TNAME="+threading.currentThread().getName()+";time="+now)
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
                    return

                # Fetches the firts 2 events
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
                            result["busynow"] = True
                            result["curevmsg"] = summary
                            result["curevend"] = datetime.strftime(endd,"%H:%M")
                            result["curevstart"] = datetime.strftime(startd,"%H:%M")
                            result["curevtm"] = result["curevstart"]+"-"+result["curevend"]
                        else:
                            #didn't start before now. will it start today ? 
                            #if starts today, calculate free until time
                            result["busynow"] = False
                            if (startd<tomorrow):
                                result["curevmsg"] = "Free until "+datetime.strftime(startd,"%H:%M")
                            else: 
                                #else is free all day
                                result["curevmsg"] = "Free all day"
                                 
                            #sets next events details
                            setNextEventDates(startd,endd,tomorrow,result)
                            result["nextevmsg"] = summary
                            
                    if evno==2:
                        #second event is useful only if room is busy to set next mtg details
                        if result["busynow"]==True:
                            result["nextevmsg"] = summary
                            setNextEventDates(startd,endd,tomorrow,result)
                            
                    evno = evno+1

                print(result)
                
                #iotclient.setThingProperty("room1","curmtg","no current meeting")

            except RuntimeError as error:
                print('An error occurred: %s' % error)

            print("Going to sleep...")
            sleep(5)



def setNextEventDates(startd,endd,tomorrow,result):
    if (startd<tomorrow):
        result["nextevstart"] = datetime.strftime(startd,"%H:%M")
        result["nextevend"] = datetime.strftime(endd,"%H:%M")
    else: 
        result["nextevstart"] = datetime.strftime(startd,"%Y-%m-%d %H:%M")
        result["nextevend"] = datetime.strftime(endd,"%H:%M")
    result["nextevtm"]=result["nextevstart"]+"-"+result["nextevend"]


