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
        
HOST = "https://api2.arduino.cc/iot"
TOKEN_URL = "https://api2.arduino.cc/iot/v1/clients/token"

def get_token():
    oauth_client = BackendApplicationClient(client_id="SOeu9scvEKBMrRjG8olnDAwegufvTiCp")
    
    oauth = OAuth2Session(client=oauth_client)
    token = oauth.fetch_token(
        token_url=TOKEN_URL,
        client_id="SOeu9scvEKBMrRjG8olnDAwegufvTiCp",
        client_secret="***REMOVED***",
        include_client_id=True,
        audience=HOST,
    )
    return token


def init_client(token):
    # configure and instance the API client
    client_config = Configuration(host=HOST)
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

        room.valid=True
    except ApiException as e:
        room.valid=False 
        print("Got an exception: {}".format(e))

    #creates cache of property ids
    #in addition to copying variables in room object
    for property in properties:
        #print(property)
        md[property.name]=property.id
        value = property.last_value
        if value is None:
            value = ""
        if property.name==PNAME_CUREVMSG:
            room.curevmsg=value
        if property.name==PNAME_BUSYNOW:
            room.busynow=value
        if property.name==PNAME_CUREVSTART:
            room.curevstart=value
        if property.name==PNAME_CUREVEND:
            room.curevend=value
        if property.name==PNAME_CUREVTM:
            room.curevtm=value
        if property.name==PNAME_NEXTEVMSG:
            room.nextevmsg=value
        if property.name==PNAME_NEXTEV_START:
            room.nextevstart=value
        if property.name==PNAME_NEXTEVTM:
            room.nextevtm=value
        if property.name==PNAME_NEXTEV_END:
            room.nextevend=value

    room.metadata=md

    return room


def update_room_status(newstatus,current):
    
    token = get_token()
    client = init_client(token)
    properties_api = iot.PropertiesV2Api(client)
    
    tid = current.metadata.get("thingid","")
    devid = current.metadata.get("deviceid","")
    if tid is None or devid is None or tid =="" or devid =="":
        print("ERROR: Unable to update status in iotcloud, no thingid or deviceid")
        return
    
    try:
        update_property(properties_api,current,newstatus,tid,devid,PNAME_CUREVMSG)
        update_property(properties_api,current,newstatus,tid,devid,PNAME_CUREVSTART)
        update_property(properties_api,current,newstatus,tid,devid,PNAME_CUREVEND)
        update_property(properties_api,current,newstatus,tid,devid,PNAME_CUREVTM)
        update_property(properties_api,current,newstatus,tid,devid,PNAME_NEXTEVMSG)
        update_property(properties_api,current,newstatus,tid,devid,PNAME_NEXTEV_START)
        update_property(properties_api,current,newstatus,tid,devid,PNAME_NEXTEV_END)
        update_property(properties_api,current,newstatus,tid,devid,PNAME_NEXTEVTM) 
        update_property(properties_api,current,newstatus,tid,devid,PNAME_BUSYNOW)

    except ApiException as e:
        print("Got an exception: {}".format(e))



def update_property(properties_api,current,newstatus,tid,devid,pname):
    pid = current.metadata.get(pname,"")
    if (pname == PNAME_BUSYNOW):
        value = newstatus.busynow
    if (pname == PNAME_CUREVMSG):
        value = newstatus.curevmsg
    if (pname == PNAME_CUREVSTART):
        value = newstatus.curevstart
    if (pname == PNAME_CUREVEND):
        value = newstatus.curevend
    if (pname == PNAME_CUREVTM):
        value = newstatus.curevtm
    if (pname == PNAME_NEXTEVMSG):
        value = newstatus.nextevmsg
    if (pname == PNAME_NEXTEV_START):
        value = newstatus.nextevstart
    if (pname == PNAME_NEXTEV_END):
        value = newstatus.nextevend
    if (pname == PNAME_NEXTEVTM):
        value = newstatus.nextevtm
    try:
        print("UPDATE: "+tid+"/"+pid+"/"+devid+"/"+pname+"="+str(value))
        properties_api.properties_v2_publish(tid,pid,{"value":value})
    except ApiException as e:
        print("Got an exception: {}".format(e))
