from threading import Thread
from poller import poller_task
import json
import mylogger

logger = mylogger.getlogger(__name__)

if __name__ == '__main__':

    logger.info("Starting backend poller...")
    logger.debug("Opening configuration on config.json")
    with open('config.json', 'r') as f:
        config = json.load(f)
    logger.debug(config)

    client_secret=config.get("iot_client_secret","")
    client_id=config.get("iot_client_id","")
    insert_asuser=config.get("gcal_insert_asuser","")

    rooms = config.get("rooms",[])
    for room in rooms:
        calendar_id = room.get("gcal_calendar_id","")
        room_name = room.get("room_name","")
        logger.info("Starting thread for room = "+room_name)    
        thread = Thread(target=poller_task, args=(calendar_id,room_name,client_id,client_secret))
        thread.start()
    
    
