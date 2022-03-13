import arduino_iot_rest as iot
from flask import jsonify

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from arduino_iot_rest.rest import ApiException
from arduino_iot_rest.configuration import Configuration

from RoomStatus import RoomStatus

PNAME_CUREVMSG = "curevmsg"
PNAME_BUSYNOW = "busynow"
PNAME_CUREVSTART="curevstart"
PNAME_CUREVEND="curevend"
PNAME_CUREVTM="curevtm"
PNAME_NEXTEVMSG="nextevmsg"
PNAME_NEXTEV_START="nextevstart"
PNAME_NEXTEVTM="nextevtm"
PNAME_NEXTEV_END="nextevend"
        

def get_token():
    oauth_client = BackendApplicationClient(client_id="SOeu9scvEKBMrRjG8olnDAwegufvTiCp")
    token_url = "https://api2.arduino.cc/iot/v1/clients/token"

    oauth = OAuth2Session(client=oauth_client)
    token = oauth.fetch_token(
        token_url=token_url,
        client_id="SOeu9scvEKBMrRjG8olnDAwegufvTiCp",
        client_secret="***REMOVED***",
        include_client_id=True,
        audience="https://api2.arduino.cc/iot",
    )
    return token


def init_client(token):
    # configure and instance the API client
    client_config = Configuration(host="https://api2.arduino.cc/iot")
    client_config.access_token = token.get("access_token")
    client = iot.ApiClient(client_config)

    return client


def get_room_status(room_name):
    token = get_token()
    client = init_client(token)
    things_api = iot.ThingsV2Api(client)
    properties_api = iot.PropertiesV2Api(client)
    
    room=RoomStatus()

    properties=[]
    md={}    
    try:
        
        things = things_api.things_v2_list()
        for thing in things:
            if thing.name == room_name:
                room.name=room_name
                md["thingid"]=thing.id
                md["deviceid"]=thing.device_id
                properties=properties_api.properties_v2_list(thing.id)

    except ApiException as e:
        print("Got an exception: {}".format(e))

    #creates cache of property ids
    #in addition to copying variables in room object
    for property in properties:
        print(property)
        md[property.name]=property.id
        if property.name==PNAME_CUREVMSG:
            room.curevmsg=property.last_value
        if property.name==PNAME_BUSYNOW:
            room.busynow=property.last_value
        if property.name==PNAME_CUREVSTART:
            room.curevstart=property.last_value
        if property.name==PNAME_CUREVEND:
            room.curevend=property.last_value
        if property.name==PNAME_CUREVTM:
            room.curevtm=property.last_value
        if property.name==PNAME_NEXTEVMSG:
            room.nextevmsg=property.last_value
        if property.name==PNAME_NEXTEV_START:
            room.nextevstart=property.last_value
        if property.name==PNAME_NEXTEVTM:
            room.nextevtm=property.last_value
        if property.name==PNAME_NEXTEV_END:
            room.nextevend=property.last_value

    room.metadata=md

    return room


def update_room_status(newstatus,current):
    
    token = get_token()
    client = init_client(token)
    properties_api = iot.PropertiesV2Api(client)
    
    result={}

    tid = current.metadata.get("thingid","")
    devid = current.metadata.get("deviceid","")
    if tid is None or devid is None or tid =="" or devid =="":
        print("ERROR: Unable to update status in iotcloud, no thingid or deviceid")
        return result

    try:
        pid = current.metadata.get(PNAME_CUREVMSG,"")
        value = newstatus.curevmsg
        print("UPDATE: "+tid+"/"+pid+"/"+devid+"/"+PNAME_CUREVMSG+"="+value)
        result = properties_api.properties_v2_publish(tid,pid,{"value":value,"device_id":devid})
        print(result)

    except ApiException as e:
        print("Got an exception: {}".format(e))

    return jsonify(result)


