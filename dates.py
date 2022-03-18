from datetime import datetime,timezone
from roomstatus import RoomStatus
import time

dt1 = datetime.now(timezone.utc)

dt2 = datetime.strptime("2022-03-12T17:00:00+01:00","%Y-%m-%dT%H:%M:%S%z")

print(dt2-dt1)

room = RoomStatus()
room.curevmsg="ciao"
print(room)

dt3 = datetime.strftime(datetime.utcnow(),"%Y-%m-%dT%H:%M:%S%z")
dt3 = datetime.strftime(datetime.utcnow(),"%a %d %b %H:%M")
print(dt3)

dt3 = datetime.now()
print(dt3.minute)

utctm = int(time.time())
print(utctm)
dt3 = datetime.utcfromtimestamp(utctm)
print(dt3)
mins = dt3.minute
mins = mins - (mins % 15)
print(mins)
dt3 = dt3.replace(minute=mins, second=0, microsecond=0)
print(dt3)

duration_mins=36
duration_mins = int(duration_mins / 15)*15
print(duration_mins)
 
