# GCalService

This service integrates with Google Calendar and provides two different functions:
* a convenient REST api to retrieve summary status for a room, and for booking the room for an immediate meeting
* an automated syncrhonization between room status in Google Calendar and a corresponding Thing status in Arduino IoTCloud

Pre-requisites in Arduino IoTCloud:
* for each room named "room_name" listed configuration, there has to be a corresponding Thing in Arduino IoTCloud with Thing name = room_name
* the Thing in IoTCloud is prepared upfront with the following variables:
   * busynow (integer) = 0 if the room is currently free, 1 if the room is currently busy
   * curevmtg (string) = "current event meeting" = description of the meeting in progress, or a sentence like "free until..." if no meeting in progress
   * curevstart (string) = start time of current meeting if any
   * curevend (string) = end time of current meeting if any
   * curevtm (string) = summary indication of time interval (e.g. 15:00-18:00) of current meeting if any
   * nextevmtg (string) = "next event meeting" = description of the next upcoming meeting in this room, if any
   * nextevstart (string) = start time of next meeting if any
   * nextevend (string) = end time of next meeting if any
   * nextevtm (string) = summary indication of time interval (e.g. 15:00-18:00) of next meeting if any
   
## Configuration 

In order to be able to talk to Google Calendar API, the following configuration must be performed:
* create a project in Google Compute Cloud
* enable Calendar API for that project
* create a serviceaccount with Editor role on the project
* create a key associated to the service account and save the credential file in JSON format as "credentials.json" in the project folder
The configuration file "credentials.json" will be used to connect to Google Calendar API

Additionally, we need to inform the program of which rooms we want to monitor and how to connect to Arduino IoTCloud.
For this prupose, create a file "config.json" with the following structure in the project folder:
``
{
    "iot_client_secret":"----your client secret here ----",
    "iot_client_id":"----your client id here ----",
    "gcal_insert_asuser":"----your user email here ----",
    "rooms":[
        {
            "room_name":"blue_room",
            "gcal_calendar_id":"----your gcal ID here ----"
        }
    ]
}
``



## REST service

* GET /meetings  - returns JSON object representing room status with next two meetings
* POST /meetings  - creates new meeting starting now 
    ** start time is rounded to 15 mins slots
    ** returns 201 if created successfully, or proper error code otherwise

Required JSON input body (for both methods)
``
{
    "room_name":"blue_room",
    "client_secret":"---YOUR IOTCLOUD CLIENT SECRET HERE---"
    "client_id":"---YOUR IOTCLOUD CLIENT ID HERE---"
}
``


## Deployment on Google Cloud platform (optional)

The code can be executed anywhere but in case you decide to deploy to Google Cloud too, some hints follow:


#configure repository
gcloud artifacts repositories create gcalsvc-bepoller-repo --repository-format=docker \
--location=us-east1 --description="backend container for gcalsvc"
gcloud auth configure-docker us-east1-docker.pkg.dev


#run BACKEND POLLER BUILD with gcloud and push to registry
#then run backend container in a dedicated machine
cp bepoller.Dockerfile Dockerfile
gcloud builds submit --tag us-east1-docker.pkg.dev/roomcalendar-343908/gcalsvc-bepoller-repo/gcalsvc-bepoller:latest

gcloud compute instances create-with-container roomcalsrv --zone us-east1-b --container-image=us-east1-docker.pkg.dev/roomcalendar-343908/gcalsvc-bepoller-repo/gcalsvc-bepoller:latest --machine-type=e2-small

gcloud compute instances update-container roomcalsrv --zone us-east1-b --container-image=us-east1-docker.pkg.dev/roomcalendar-343908/gcalsvc-bepoller-repo/gcalsvc-bepoller:latest


#allow serviceaccount to access secrets

gcloud secrets add-iam-policy-binding roomcal-config-json \
    --member="serviceAccount:roomcal-gcalsvc@roomcalendar-343908.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding roomcal-gcal-credentials \
    --member="serviceAccount:roomcal-gcalsvc@roomcalendar-343908.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"


#build and run frontend server
cp frontend.Dockerfile Dockerfile
#gcloud builds submit --tag us-east1-docker.pkg.dev/roomcalendar-343908/cloud-run-source-deploy/gcalsvc:latest
gcloud run deploy --max-instances 1 --allow-unauthenticated \
--service-account=roomcal-gcalsvc@roomcalendar-343908.iam.gserviceaccount.com --source .

####
gcloud run deploy --max-instances 1 --allow-unauthenticated --service-account=roomcal-gcalsvc@roomcalendar-343908.iam.gserviceaccount.com --update-secrets=/isecrets/config.json=roomcal-config-json:latest,/gsecrets/credentials.json=roomcal-gcal-credentials:latest --source .


gcloud run deploy gcalsvc \
--image=us-east1-docker.pkg.dev/roomcalendar-343908/cloud-run-source-deploy/gcalsvc \
--service-account=roomcal-gcalsvc@roomcalendar-343908.iam.gserviceaccount.com \
--platform=managed \
--region=us-east1 \
--project=roomcalendar-343908 \
 && gcloud run services update-traffic gcalsvc --to-latest




#did not use the ones below
#build BACKEND POLLER CONTAINER
docker build -f bepoller.Dockerfile . --tag us-east1-docker.pkg.dev/roomcalendar-343908/gcalsvc-bepoller-repo/gcalsvc-bepoller:latest
docker push us-east1-docker.pkg.dev/roomcalendar-343908/gcalsvc-bepoller-repo/gcalsvc-bepoller:latest

docker build -f bepoller.Dockerfile . --tag us-gcr.io/roomcalendar-343908/gcalsvc-bepoller:latest
docker push us-gcr.io/roomcalendar-343908/gcalsvc-bepoller:latest
