# CortexGIS Cloud Deployment Guides

Complete instructions for deploying CortexGIS to major cloud platforms.

---

## AWS Deployment

### Option 1: EC2 + Docker

#### Prerequisites
- AWS Account
- EC2 security group with port 8501 open
- EC2 key pair (.pem file)

#### Steps

1. **Launch EC2 Instance:**

```bash
# Via AWS Console or CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.small \
  --key-name my-key \
  --security-groups default \
  --region us-east-1
```

2. **SSH into instance:**

```bash
ssh -i my-key.pem ec2-user@<public-ip>
```

3. **Install Docker:**

```bash
sudo yum update -y
sudo yum install docker git -y
sudo systemctl start docker
sudo usermod -aG docker ec2-user
```

4. **Deploy CortexGIS:**

```bash
git clone https://github.com/yourusername/cortexgis.git
cd cortexgis

# Option A: Docker Compose
docker-compose up -d

# Option B: Docker run
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/outputs:/cortexgis/outputs \
  --name cortexgis \
  cortexgis:latest
```

5. **Access app:**

Navigate to `http://<public-ip>:8501`

### Option 2: AWS Elastic Beanstalk

1. **Create `.ebextensions/python.config`:**

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:application
  aws:elasticbeanstalk:application:environment:
    STREAMLIT_SERVER_PORT: 8501
```

2. **Deploy:**

```bash
eb create cortexgis-env --instance-type t3.small
eb deploy
eb open
```

### Option 3: AWS Lambda + API Gateway

For serverless inference only (not UI):

```python
# lambda_handler.py
from planner.geospatial_planner import GeospatialPlanner
from executor.executor import WorkflowExecutor

planner = GeospatialPlanner()
executor = WorkflowExecutor()

def lambda_handler(event, context):
    query = event.get("query")
    cot, workflow = planner.plan_workflow(query)
    result = executor.execute_workflow(workflow)
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
```

Deploy with `serverless-framework` or AWS SAM.

---

## Google Cloud Platform

### Option 1: Cloud Run (Recommended)

Easiest for Streamlit apps.

1. **Build and push Docker image:**

```bash
gcloud auth login
gcloud config set project my-project-id

# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/my-project-id/cortexgis:latest
```

2. **Deploy to Cloud Run:**

```bash
gcloud run deploy cortexgis \
  --image gcr.io/my-project-id/cortexgis:latest \
  --platform managed \
  --region us-central1 \
  --port 8501 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600
```

3. **Access app:**

```bash
gcloud run services describe cortexgis --platform managed
# Copy the URL and navigate to it
```

### Option 2: Compute Engine + Docker

Similar to AWS EC2:

```bash
# Create instance
gcloud compute instances create cortexgis \
  --image-family debian-11 \
  --image-project debian-cloud \
  --machine-type e2-medium \
  --zone us-central1-a

# SSH in
gcloud compute ssh cortexgis

# Install and run Docker
curl https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

git clone https://github.com/yourusername/cortexgis.git
cd cortexgis
docker-compose up -d
```

### Option 3: Vertex AI (For ML workloads)

Deploy ML components to Vertex AI for scalability:

```python
from google.cloud import aiplatform

def deploy_to_vertex():
    aiplatform.init(project="my-project", location="us-central1")
    
    model = aiplatform.Model.upload(
        display_name="cortexgis-planner",
        artifact_uri="gs://my-bucket/models/",
        serving_container_image_uri="gcr.io/my-project/cortexgis:latest"
    )
    
    endpoint = model.deploy(machine_type="n1-standard-4")
    return endpoint
```

---

## Microsoft Azure

### Option 1: Container Instances

Quick and easy:

```bash
az login
az group create --name cortexgis-rg --location eastus

# Push image to ACR
az acr build -r myregistry -t cortexgis:latest .

# Deploy to Container Instances
az container create \
  --resource-group cortexgis-rg \
  --name cortexgis \
  --image myregistry.azurecr.io/cortexgis:latest \
  --registry-login-server myregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --ports 8501 \
  --ip-address public
```

### Option 2: Azure App Service

```bash
# Create App Service Plan
az appservice plan create \
  --name cortexgis-plan \
  --resource-group cortexgis-rg \
  --sku B2 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group cortexgis-rg \
  --plan cortexgis-plan \
  --name cortexgis-app \
  --deployment-container-image-name myregistry.azurecr.io/cortexgis:latest

# Configure
az webapp config container set \
  --name cortexgis-app \
  --resource-group cortexgis-rg \
  --docker-custom-image-name myregistry.azurecr.io/cortexgis:latest
```

### Option 3: Azure Kubernetes Service (AKS)

For production at scale:

```bash
# Create AKS cluster
az aks create \
  --resource-group cortexgis-rg \
  --name cortexgis-aks \
  --node-count 3 \
  --attach-acr myregistry

# Deploy with Helm
helm install cortexgis ./charts/cortexgis \
  --set image.repository=myregistry.azurecr.io/cortexgis
```

---

## Kubernetes (Self-Managed)

### Prerequisites
- Kubernetes cluster (minikube, EKS, GKE, AKS, etc.)
- `kubectl` installed
- Docker image pushed to registry

### Deployment

1. **Create namespace:**

```bash
kubectl create namespace cortexgis
```

2. **Create Deployment:**

```yaml
# cortexgis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cortexgis
  namespace: cortexgis
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cortexgis
  template:
    metadata:
      labels:
        app: cortexgis
    spec:
      containers:
      - name: cortexgis
        image: myregistry/cortexgis:latest
        ports:
        - containerPort: 8501
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: cortexgis-secrets
              key: openai-api-key
        volumeMounts:
        - name: outputs
          mountPath: /cortexgis/outputs
      volumes:
      - name: outputs
        emptyDir: {}
```

3. **Create Service:**

```yaml
# cortexgis-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: cortexgis
  namespace: cortexgis
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8501
  selector:
    app: cortexgis
```

4. **Deploy:**

```bash
kubectl apply -f cortexgis-deployment.yaml
kubectl apply -f cortexgis-service.yaml

# View status
kubectl get pods -n cortexgis
kubectl get svc -n cortexgis
```

5. **Access app:**

```bash
kubectl port-forward -n cortexgis svc/cortexgis 8501:80
# Visit http://localhost:8501
```

---

## Heroku (Deprecated, Alternative: Railway)

Heroku free tier discontinued, but Railway is a good alternative:

```bash
# Install railway
npm i -g @railway/cli

# Login
railway login

# Deploy
railway init
railway up
```

---

## Self-Hosted (VPS)

### Using DigitalOcean, Linode, or Other VPS

1. **Provision Droplet/Linode:**
   - 2GB RAM, 1 vCPU minimum
   - Ubuntu 20.04 or later

2. **SSH and setup:**

```bash
ssh root@<ip>

# Update system
apt update && apt upgrade -y
apt install -y docker.io docker-compose git
systemctl start docker

# Clone and deploy
git clone https://github.com/yourusername/cortexgis.git
cd cortexgis
docker-compose up -d
```

3. **Setup reverse proxy (Nginx):**

```nginx
# /etc/nginx/sites-available/cortexgis
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

4. **Enable HTTPS (Let's Encrypt):**

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com
```

---

## Environment-Specific Configuration

### Production `.env`

```bash
# Production deployment
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_MAXUPLOADSIZE=2048  # MB
STREAMLIT_LOGGER_LEVEL=warning
PYTHONUNBUFFERED=1

# LLM (use production-grade API)
OPENAI_API_KEY=sk-...
OPENAI_API_BASE=https://api.openai.com/v1

# Data (use cloud storage)
OUTPUT_DIR=s3://my-bucket/outputs
DATA_DIR=gs://my-data-bucket

# Logging (use managed service)
LOG_LEVEL=INFO
LOG_FILE=/var/log/cortexgis/app.log

# Security
ALLOWED_ORIGINS=https://yourdomain.com
SECRET_KEY=<generate-random-key>
```

### Monitoring & Logging

```bash
# CloudWatch (AWS)
pip install watchtower
import logging
import watchtower
logging.basicConfig(handlers=[watchtower.CloudWatchLogHandler()])

# Datadog
pip install datadog
from datadog import initialize, api

# Application Insights (Azure)
pip install opencensus-ext-azure
```

---

## Cost Estimates (Approximate, Q4 2024)

| Platform | Service | Monthly Cost (Minimal) | Details |
|----------|---------|------------------------|---------|
| **AWS** | EC2 t3.micro | $7-10 | 1GB RAM, ~750hrs/month free tier |
| **AWS** | Lambda | $0.20 | 1M invocations, mostly free |
| **GCP** | Cloud Run | $0.50 | 2M free requests, $0.40/M after |
| **Azure** | Container Instances | $15-20 | 1 vCPU, 1GB RAM, always on |
| **Heroku** | (Discontinued) | N/A | Use Railway: ~$7-10 |
| **Railway** | Starter | $5-20 | Simple apps, pay for usage |
| **DigitalOcean** | Droplet | $4-12 | 512MB-2GB RAM; $5/month popular |
| **Kubernetes** | (Any cloud) | $30-100 | Per month for managed cluster |

---

## Performance Tips

- **Add caching:** Use Redis for workflow caching
- **Scale horizontally:** Use Kubernetes or load balancers
- **Optimize data:** Use cloud-native formats (Parquet, COG)
- **Monitor:** Use cloud-native APM tools
- **Cache ML models:** Load once, reuse across requests
- **Use CDN:** For static assets and outputs

---

## Troubleshooting Deployments

| Issue | Solution |
|-------|----------|
| Port already in use | Change port in `.env`: `STREAMLIT_SERVER_PORT=8502` |
| Memory issues | Increase container limits; optimize data loading |
| Slow startup | Pre-download ML models; cache initialization |
| API key exposure | Use secrets manager (AWS Secrets, Azure Key Vault, etc.) |
| Network timeouts | Increase timeout; check firewall rules |
| CORS errors | Configure `ALLOWED_ORIGINS` in app |

---

## Next Steps

1. Choose deployment platform based on budget & scale
2. Prepare `.env` file with secrets
3. Push Docker image to registry
4. Test locally with `docker-compose up`
5. Deploy and monitor logs
6. Setup monitoring/alerting
7. Configure custom domain & HTTPS

---

**Happy deploying! 🚀**
