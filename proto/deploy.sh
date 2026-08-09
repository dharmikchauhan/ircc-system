export PROJECT_ID="tmp-project-20"
export REGION="australia-southeast1"
export SERVICE_NAME="ircc-agent-service"
export TOPIC_NAME="telemetry.stockout.v1"
export SERVICE_ACCOUNT_NAME="agent-runner"
export WORKFLOW_NAME="ircc-workflow"
export SA_DISPLAY_NAME="IRCC Agent Runner"
export AGENT_NAME="ircc_agent"

echo "-- Setting up IRCC Agent on Google Cloud --"

# Set project
gcloud config set project $PROJECT_ID
echo "--> 1. Project set to $PROJECT_ID"

# Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com aiplatform.googleapis.com workflows.googleapis.com eventarc.googleapis.com pubsub.googleapis.com
echo "--> 2. Required APIs enabled"

# Create pub/sub topic
gcloud pubsub topics create $TOPIC_NAME
echo "--> 3. Pub/Sub Topic created: $TOPIC_NAME"

# Deploy adk agent to cloud run
.venv/bin/adk deploy cloud_run ircc_agent \
  --service_name=$SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  -- \
  --quiet \
  --no-allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your-key \
  --set-env-vars GOOGLE_GENAI_USE_ENTERPRISE=0 \
  --set-env-vars GOOGLE_CLOUD_LOCATION=global \
  --set-env-vars ADK_DEFAULT_APP_NAME=ircc_agent

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo "--> 4. Service deployed on Cloud Run: $SERVICE_URL"

# Create service account and grant permission to invoke Cloud Run
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
  --display-name=$SA_DISPLAY_NAME

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --role="roles/eventarc.eventReceiver" \
  --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --role="roles/workflows.invoker" \
  --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --role="roles/iam.serviceAccountTokenCreator" \
  --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --role="roles/logging.logWriter" \
  --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --role="roles/run.invoker" \
  --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "--> 5. Service account $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com created and attached to $SERVICE_NAME"

# CLOUD WORKFLOW
gcloud workflows deploy $WORKFLOW_NAME \
  --source=../specialization/workflow.yaml \
  --location=$REGION \
  --service-account="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "--> 6. Workflow deployed: ircc-workflow"

# Create Eventarc Trigger linking Pub/Sub to Workflows
gcloud eventarc triggers create $WORKFLOW_NAME-trigger \
  --location=$REGION \
  --destination-workflow=$WORKFLOW_NAME \
  --destination-workflow-location=$REGION \
  --event-filters="type=google.cloud.pubsub.topic.v1.messagePublished" \
  --transport-topic=projects/${PROJECT_ID}/topics/${TOPIC_NAME} \
  --service-account="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "--> 7. Eventarc trigger created: $WORKFLOW_NAME-trigger"

# gcloud pubsub subscriptions create "${TOPIC_NAME}-sub" \
#   --topic=$TOPIC_NAME \
#   --push-endpoint="${SERVICE_URL}/apps/${AGENT_NAME}/trigger/pubsub" \
#   --push-auth-service-account="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
# echo "--> 6. Subscription created: $SERVICE_NAME-sub"

echo "-- IRCC Agent setup on Google Cloud completed --"