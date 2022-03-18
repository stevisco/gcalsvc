from threading import Thread

from poller import poller_task

if __name__ == '__main__':
    calendar_id='arduino.cc_3931313135363730363336@resource.calendar.google.com'
    room_name="blue_room"
    client_secret="***REMOVED***"
    client_id="SOeu9scvEKBMrRjG8olnDAwegufvTiCp"

    print("Starting threads")    
    thread = Thread(target=poller_task, args=(calendar_id,room_name,client_id,client_secret))
    thread.start()
    #thread2 = Thread(target=poller_task, args=(app,))
    #thread2.start()    
    
