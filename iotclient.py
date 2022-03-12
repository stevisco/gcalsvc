import arduino_iot_rest as iot
from flask import jsonify

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from arduino_iot_rest.rest import ApiException
from arduino_iot_rest.configuration import Configuration


def getToken():
    print("getToken")

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


def initClient(token):
    print("initClient")

    # configure and instance the API client
    client_config = Configuration(host="https://api2.arduino.cc/iot")
    client_config.access_token = token.get("access_token")
    client = iot.ApiClient(client_config)

    return client


def setThingProperty(thing_name,property_name,value):
    
    token = getToken()
    client = initClient(token)
    things_api = iot.ThingsV2Api(client)
    properties_api = iot.PropertiesV2Api(client)
    
    #TODO: retrieve tid, pid, devid based on input params
    tid = "aaa"
    pid = "aaa"
    devid = "aaa"

    result={}

    try:
        print("setThingProperty")

        result = properties_api.properties_v2_publish(tid,pid,{"value":value,"device_id":devid})
        print(result)

    except ApiException as e:
        print("Got an exception: {}".format(e))

    return jsonify(result)


