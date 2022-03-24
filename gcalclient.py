from roomstatus import RoomStatus
from datetime import datetime,timezone,timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import socket
 
SCOPES = ['https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events']


class GCalClient:

    calendarId =""
    room_name="" 

    def __init__(self,calendarId,room_name):
        self.calendarId=calendarId
        self.room_name=room_name
        return


    def set_nextev_dates(self,startd,endd,tomorrow,result):
        #utility to set next events dates in right format
        #if it's within the day use only H:M otherwise put day in front
        if (startd<tomorrow):
            result.nextevstart = datetime.strftime(startd,"%H:%M")
            result.nextevend = datetime.strftime(endd,"%H:%M")
            result.nextevtm=result.nextevstart+"-"+result.nextevend
        else: 
            result.nextevstart = datetime.strftime(startd,"%Y-%m-%d %H:%M")
            result.nextevend = datetime.strftime(endd,"%H:%M")
            result.nextevtm = datetime.strftime(startd,"%a %d %b %H:%M") \
                            +"-"+result.nextevend
 

    def get_calendar_status(self):
        result = RoomStatus()
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time    
        try:
            creds = service_account.Credentials.from_service_account_file(
                "/etc/secrets/credentials.json", scopes=SCOPES)
        
            service = build('calendar', 'v3', credentials=creds)
        
            #print('Getting the upcoming events')
            events_result = service.events().list(
                    calendarId=self.calendarId,  \
                    timeMin=now,  \
                    maxResults=2, singleEvents=True,   \
                    orderBy='startTime').execute()
            
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')
                result.valid = False 
                return result

            # Fetches the firts 2 events
            result.name=self.room_name
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
                        self.set_nextev_dates(startd,endd,tomorrow,result)
                        result.nextevmsg = summary
                        
                if evno==2:
                    #second event is useful only if room is busy to set next mtg details
                    if result.busynow==RoomStatus.BUSY:
                        result.nextevmsg = summary
                        self.set_nextev_dates(startd,endd,tomorrow,result)
                        
                evno = evno+1

            result.valid = True 
        except (RuntimeError,TimeoutError,socket.timeout) as error:
            result.valid = False 
            print('GCALCLIENT: An error occurred: %s' % error)
        
        return result



    def insert_instantmeeting(self,duration_mins,insert_asuser):
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
                "/etc/secrets/credentials.json", scopes=SCOPES)
            creds = creds.with_subject(insert_asuser)
        
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
            event = service.events().insert(calendarId=self.calendarId, body=event).execute() 
            return True

        except (RuntimeError,TimeoutError,socket.timeout,HttpError) as error:
            print('GCALCLIENT: An error occurred: %s' % error)
            return False
