# Deployment Guide

This guide explains how to deploy the superconducting materials discovery pipeline on AWS, GCP, or Azure using Docker, Kubernetes, and CI/CD.

## Prerequisites

- Docker installed locally
- kubectl configured for your cluster
- Cloud provider CLI (aws, gcloud, az) installed and authenticated
- GitHub repository with CI/CD enabled

## 1. Docker Image

Build the pipeline image:

```bash
docker build -t supercon-pipeline:latest .
```

Tag and push to your container registry:

- **AWS ECR**:
  ```bash
  aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
  docker tag supercon-pipeline:latest <account>.dkr.ecr.us-east-1.amazonaws.com/supercon-pipeline:latest
  docker push <account>.dkr.ecr.us-east-1.amazonaws.com/supercon-pipeline:latest
  ```

- **GCP GCR**:
  ```bash
  gcloud auth configure-docker
  docker tag supercon-pipeline:latest gcr.io/<project-id>/supercon-pipeline:latest
  docker push gcr.io/<project-id>/supercon-pipeline:latest
  ```

- **Azure ACR**:
  ```bash
  az acr login --name <registry-name>
  docker tag supercon-pipeline:latest <registry-name>.azurecr.io/supercon-pipeline:latest
  docker push <registry-name>.azurecr.io/supercon-pipeline:latest
  ```

## 2. Kubernetes Deployment

Create a namespace:

```bash
kubectl create namespace supercon
```

Apply the deployment manifest (`k8s/deployment.yaml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: supercon-pipeline
  namespace: supercon
spec:
  replicas: 1
  selector:
    matchLabels:
      app: supercon-pipeline
  template:
    metadata:
      labels:
        app: supercon-pipeline
    spec:
      containers:
      - name: pipeline
        image: <your-registry>/supercon-pipeline:latest
        env:
        - name: SUPERCON_API_KEY
          valueFrom:
            secretKeyRef:
              name: supercon-secrets
              key: api-key
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
```

Apply:

```bash
kubectl apply -f k8s/deployment.yaml
```

For scheduled runs, use a CronJob:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: supercon-pipeline-cron
  namespace: supercon
spec:
  schedule: "0 6 * * *"  # daily at 6 AM UTC
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: pipeline
            image: <your-registry>/supercon-pipeline:latest
            command: ["python", "run_pipeline.py"]
          restartPolicy: OnFailure
```

## 3. CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Pipeline

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build Docker image
      run: docker build -t supercon-pipeline:${{ github.sha }} .
    - name: Push to registry
      run: |
        # Use cloud-specific login (example for AWS ECR)
        aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${{ secrets.AWS_ACCOUNT }}.dkr.ecr.us-east-1.amazonaws.com
        docker tag supercon-pipeline:${{ github.sha }} ${{ secrets.AWS_ACCOUNT }}.dkr.ecr.us-east-1.amazonaws.com/supercon-pipeline:latest
        docker push ${{ secrets.AWS_ACCOUNT }}.dkr.ecr.us-east-1.amazonaws.com/supercon-pipeline:latest
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/supercon-pipeline pipeline=${{ secrets.AWS_ACCOUNT }}.dkr.ecr.us-east-1.amazonaws.com/supercon-pipeline:latest -n supercon
```

## 4. Cloud-Specific Notes

### AWS
- Use EKS for managed Kubernetes.
- Store secrets in AWS Secrets Manager and sync to Kubernetes with external-secrets.
- Use S3 for data storage (candidates, results).

### GCP
- Use GKE for managed Kubernetes.
- Use Cloud Storage for data.
- Use Cloud Scheduler to trigger CronJobs.

### Azure
- Use AKS for managed Kubernetes.
- Use Blob Storage for data.
- Use Azure Container Instances for burst jobs.

## 5. Monitoring

- Enable Kubernetes Dashboard or use `kubectl logs`.
- Set up Prometheus/Grafana for metrics.
- Configure alerts for pipeline failures.

## 6. Scaling

- Increase replicas for parallel candidate screening.
- Use node pools with GPU instances for DFT calculations.
- Adjust resource limits in deployment manifest.

## 7. Troubleshooting

- Check pod logs: `kubectl logs -n supercon <pod-name>`
- Verify secrets: `kubectl get secrets -n supercon`
- Test connectivity: `kubectl exec -it -n supercon <pod-name> -- /bin/sh`

---

*This guide is part of the superconducting materials discovery project. For questions, refer to the project README.*

## 8. Automated Docker Build

The project includes an automated Docker build function (`scripts/automated_docker_build.py`) that builds and pushes the image to Docker Hub. To use it:

### Configure Docker Hub Credentials

Set the following environment variables or add them to your CI/CD secrets:

- `DOCKER_USERNAME` – your Docker Hub username
- `DOCKER_PASSWORD` – your Docker Hub password or access token

Alternatively, run `docker login` manually:

```bash
docker login -u <username> -p <password>
```

### Run the Automated Build

Execute the build script:

```bash
python scripts/automated_docker_build.py
```

The script will:
- Build the Docker image with the tag `supercon-pipeline:latest`
- Tag it with the current commit SHA
- Push both tags to Docker Hub under your username

### CI/CD Integration

In your GitHub Actions workflow, add the following step after checkout:

```yaml
- name: Build and push to Docker Hub
  env:
    DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
    DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
  run: python scripts/automated_docker_build.py
```

Make sure to add `DOCKER_USERNAME` and `DOCKER_PASSWORD` as secrets in your GitHub repository settings.


## 9. Environment Variables for Registry Credentials

To simplify Docker image generation and pushing, set the following environment variables for your container registry. These can be used in local scripts or CI/CD pipelines.

### Docker Hub
- `DOCKER_USERNAME` – your Docker Hub username
- `DOCKER_PASSWORD` – your Docker Hub password or access token

Example local setup:
```bash
export DOCKER_USERNAME=myuser
export DOCKER_PASSWORD=mypassword
```

### AWS ECR
- `AWS_ACCOUNT` – your 12-digit AWS account ID
- `AWS_REGION` – the AWS region (e.g., `us-east-1`)
- `AWS_ACCESS_KEY_ID` – IAM access key (if not using instance profile)
- `AWS_SECRET_ACCESS_KEY` – IAM secret key

Example:
```bash
export AWS_ACCOUNT=123456789012
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...
```

Then use in scripts:
```bash
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
docker tag supercon-pipeline:latest $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/supercon-pipeline:latest
docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/supercon-pipeline:latest
```

### GCP GCR
- `GCP_PROJECT_ID` – your Google Cloud project ID
- `GCP_SERVICE_ACCOUNT_KEY` – path to a JSON key file (optional, for CI/CD)

Example:
```bash
export GCP_PROJECT_ID=my-project-123
gcloud auth configure-docker --quiet
docker tag supercon-pipeline:latest gcr.io/$GCP_PROJECT_ID/supercon-pipeline:latest
docker push gcr.io/$GCP_PROJECT_ID/supercon-pipeline:latest
```

### Azure ACR
- `AZURE_REGISTRY_NAME` – your Azure Container Registry name
- `AZURE_CLIENT_ID` – service principal client ID (optional)
- `AZURE_CLIENT_SECRET` – service principal secret (optional)
- `AZURE_TENANT_ID` – Azure AD tenant ID (optional)

Example:
```bash
export AZURE_REGISTRY_NAME=myregistry
export AZURE_CLIENT_ID=...
export AZURE_CLIENT_SECRET=...
export AZURE_TENANT_ID=...
az acr login --name $AZURE_REGISTRY_NAME
docker tag supercon-pipeline:latest $AZURE_REGISTRY_NAME.azurecr.io/supercon-pipeline:latest
docker push $AZURE_REGISTRY_NAME.azurecr.io/supercon-pipeline:latest
```

### CI/CD Secrets
In GitHub Actions, add the relevant variables as repository secrets (e.g., `AWS_ACCOUNT`, `DOCKER_USERNAME`, `GCP_PROJECT_ID`, `AZURE_REGISTRY_NAME`) and reference them in your workflow as `${{ secrets.VAR_NAME }}`.
