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
