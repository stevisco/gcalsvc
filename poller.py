import datetime
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



def poller_task(app):
    with app.app_context():
        
        while True:
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
                
            print("TNAME="+threading.currentThread().getName()+";time="+now)
            try:
                creds = service_account.Credentials.from_service_account_file(
                    "credentials.json", scopes=SCOPES)
            
                service = build('calendar', 'v3', credentials=creds)

                print('Getting the upcoming 5 events')
                events_result = service.events().list(
                        calendarId='arduino.cc_3931313135363730363336@resource.calendar.google.com', 
                        timeMin=now,
                        maxResults=5, singleEvents=True,
                        orderBy='startTime').execute()
                events = events_result.get('items', [])

                if not events:
                    print('No upcoming events found.')
                    return

                # Prints the start and name of the next 5 events
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    summary = "unknown"
                    if "summary" in event:
                            summary = event["summary"]
                    print(start, summary)
                
                iotclient.setThingProperty("room1","curmtg","no current meeting")

            except RuntimeError as error:
                print('An error occurred: %s' % error)

            print("Going to sleep...")
            sleep(5)
