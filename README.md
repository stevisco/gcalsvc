# gcalsvc


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

#build BACKEND POLLER CONTAINER
gcloud auth configure-docker us-east1-docker.pkg.dev
docker build -f bepoller.Dockerfile . --tag us-east1-docker.pkg.dev/roomcalendar-343908/cloud-run-source-deploy/gcalsvc-bepoller:latest
docker push us-east1-docker.pkg.dev/roomcalendar-343908/cloud-run-source-deploy/gcalsvc-bepoller:latest


#build and run frontend server
gcloud builds submit --tag us-east1-docker.pkg.dev/roomcalendar-343908/cloud-run-source-deploy/gcalsvc:latest
gcloud run deploy --max-instances 1 --source .


gcloud compute instances create-with-container roomcalsrv --zone us-east1-b --container-image=us-east1-docker.pkg.dev/roomcalendar-343908/cloud-run-source-deploy/gcalsvc:latest --machine-type=e2-small

gcloud run deploy --no-cpu-throttling --max-instances 1 --source .


- create instance group
- create load balancer that takes HTTPS in