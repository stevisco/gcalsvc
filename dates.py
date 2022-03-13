from datetime import datetime,timezone
from RoomStatus import RoomStatus

dt1 = datetime.now(timezone.utc)

dt2 = datetime.strptime("2022-03-12T17:00:00+01:00","%Y-%m-%dT%H:%M:%S%z")

print(dt2-dt1)

room = RoomStatus()
room.curevmsg="ciao"
print(room)

room2 = RoomStatus()
room2.curevmsg="ciao"
print(room2)

if room==room2:
    print("EQUAL!")
else:
    print("DIFFERENT!")

