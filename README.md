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
