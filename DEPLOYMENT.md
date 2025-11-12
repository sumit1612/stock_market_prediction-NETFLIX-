# Deployment Guide

This guide covers different deployment options for the Netflix Stock Prediction application.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [AWS ECS with Fargate](#aws-ecs-with-fargate)
4. [AWS Elastic Beanstalk](#aws-elastic-beanstalk)
5. [AWS EC2](#aws-ec2)

## Local Development

### Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your TIINGO_API_KEY

# Run backend
python main.py
```

Backend will be available at `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend will be available at `http://localhost:3000`

## Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed

### Steps

1. **Create environment file**

```bash
cat > .env << EOF
TIINGO_API_KEY=your_actual_api_key_here
TIME_STEP=100
TRAINING_SIZE_RATIO=0.65
LSTM_UNITS=50
EPOCHS=100
BATCH_SIZE=64
EOF
```

2. **Build and run**

```bash
docker-compose up --build -d
```

3. **Access the application**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

4. **View logs**

```bash
docker-compose logs -f
```

5. **Stop the application**

```bash
docker-compose down
```

## AWS ECS with Fargate

### Prerequisites
- AWS CLI configured
- AWS account with appropriate permissions
- Docker installed

### Option 1: Using CloudFormation

This deploys the complete infrastructure including VPC, subnets, ALB, ECS cluster, and services.

```bash
# 1. Deploy infrastructure
aws cloudformation create-stack \
  --stack-name stock-prediction-infra \
  --template-body file://aws/cloudformation-template.yaml \
  --parameters \
    ParameterKey=EnvironmentName,ParameterValue=production \
    ParameterKey=TiingoAPIKey,ParameterValue=YOUR_API_KEY \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# 2. Wait for stack creation
aws cloudformation wait stack-create-complete \
  --stack-name stock-prediction-infra \
  --region us-east-1

# 3. Get the load balancer DNS
aws cloudformation describe-stacks \
  --stack-name stock-prediction-infra \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
  --output text
```

### Option 2: Manual ECS Deployment

#### Step 1: Create ECR Repositories

```bash
aws ecr create-repository --repository-name stock-prediction --region us-east-1
aws ecr create-repository --repository-name stock-prediction-frontend --region us-east-1
```

#### Step 2: Build and Push Images

```bash
# Get your AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="us-east-1"

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build and push backend
docker build -t stock-prediction:latest .
docker tag stock-prediction:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/stock-prediction:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/stock-prediction:latest

# Build and push frontend
docker build -f frontend/Dockerfile.frontend -t stock-prediction-frontend:latest frontend/
docker tag stock-prediction-frontend:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/stock-prediction-frontend:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/stock-prediction-frontend:latest
```

#### Step 3: Create Secrets in AWS Secrets Manager

```bash
aws secretsmanager create-secret \
  --name production-tiingo-api-key \
  --secret-string "your_tiingo_api_key" \
  --region us-east-1
```

#### Step 4: Update Task Definition

Edit `aws/ecs-task-definition.json` and replace:
- `YOUR_ACCOUNT_ID` with your AWS account ID
- `YOUR_ECR_REPO` with your ECR repository URI
- `REGION` with your AWS region
- Secret ARN with your actual secret ARN

#### Step 5: Register Task Definition

```bash
aws ecs register-task-definition \
  --cli-input-json file://aws/ecs-task-definition.json \
  --region us-east-1
```

#### Step 6: Create ECS Service

```bash
aws ecs create-service \
  --cluster production-cluster \
  --service-name stock-prediction-service \
  --task-definition stock-prediction-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=stock-prediction-backend,containerPort=8000" \
  --region us-east-1
```

### Option 3: Using Deployment Script

```bash
# Make script executable
chmod +x aws/deploy.sh

# Edit the script to set your configuration
# Then run:
./aws/deploy.sh
```

## AWS Elastic Beanstalk

### Prerequisites
- EB CLI installed: `pip install awsebcli`
- AWS credentials configured

### Steps

1. **Initialize Elastic Beanstalk**

```bash
eb init -p docker stock-prediction --region us-east-1
```

2. **Create environment**

```bash
eb create production-env \
  --instance-type t3.medium \
  --envvars TIINGO_API_KEY=your_api_key_here
```

3. **Deploy application**

```bash
eb deploy
```

4. **Open in browser**

```bash
eb open
```

5. **View logs**

```bash
eb logs
```

6. **Update environment variables**

```bash
eb setenv TIINGO_API_KEY=new_key EPOCHS=50
```

7. **Terminate when done**

```bash
eb terminate production-env
```

## AWS EC2

### Prerequisites
- EC2 instance running (t3.medium or larger recommended)
- SSH access to the instance
- Security group allowing ports 22, 80, 8000

### Steps

1. **Connect to EC2**

```bash
ssh -i your-key.pem ec2-user@your-instance-ip
```

2. **Install Docker and Docker Compose**

```bash
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. **Clone repository**

```bash
git clone <your-repo-url>
cd stock_market_prediction-NETFLIX-
```

4. **Create .env file**

```bash
cat > .env << EOF
TIINGO_API_KEY=your_api_key_here
EOF
```

5. **Run application**

```bash
docker-compose up -d
```

6. **Access application**

Visit `http://your-instance-ip:8000` for API and `http://your-instance-ip:3000` for frontend

7. **Set up as systemd service (optional)**

```bash
sudo cat > /etc/systemd/system/stock-prediction.service << EOF
[Unit]
Description=Stock Prediction Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ec2-user/stock_market_prediction-NETFLIX-
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ec2-user

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable stock-prediction
sudo systemctl start stock-prediction
```

## Environment Variables

Required environment variables for all deployments:

```env
TIINGO_API_KEY=your_api_key        # Required
TIME_STEP=100                       # Optional
TRAINING_SIZE_RATIO=0.65           # Optional
LSTM_UNITS=50                       # Optional
EPOCHS=100                          # Optional
BATCH_SIZE=64                       # Optional
API_HOST=0.0.0.0                   # Optional
API_PORT=8000                       # Optional
```

## Monitoring and Troubleshooting

### Check Container Logs

```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f frontend

# ECS
aws ecs describe-tasks --cluster your-cluster --tasks task-id
aws logs tail /ecs/stock-prediction --follow
```

### Health Checks

```bash
# Backend health
curl http://your-host:8000/health

# Check API status
curl http://your-host:8000/api/status
```

### Common Issues

**Issue**: Container fails to start
**Solution**: Check logs and environment variables

**Issue**: Cannot connect to backend from frontend
**Solution**: Verify network configuration and CORS settings

**Issue**: Out of memory
**Solution**: Increase instance size or reduce BATCH_SIZE

**Issue**: Training timeout
**Solution**: Reduce EPOCHS or increase timeout settings

## Scaling Considerations

### Horizontal Scaling
- ECS: Increase desired task count
- Add multiple instances behind load balancer

### Vertical Scaling
- Increase instance type (more CPU/RAM)
- Adjust BATCH_SIZE and other parameters

### Cost Optimization
- Use spot instances for non-critical environments
- Implement auto-scaling based on metrics
- Use S3 for model storage instead of EFS

## Security Best Practices

1. **Never commit secrets**
   - Use `.env` files locally
   - Use AWS Secrets Manager in production

2. **Use HTTPS**
   - Set up SSL/TLS certificates
   - Use AWS Certificate Manager

3. **Restrict access**
   - Use security groups
   - Implement authentication
   - Whitelist specific IPs if needed

4. **Regular updates**
   - Keep dependencies updated
   - Apply security patches
   - Monitor for vulnerabilities

## Backup and Recovery

### Model Backups

```bash
# Backup models to S3
aws s3 sync ./models s3://your-bucket/models/$(date +%Y%m%d)/

# Restore models
aws s3 sync s3://your-bucket/models/latest/ ./models/
```

### Data Backups

```bash
# Backup data
aws s3 sync ./data s3://your-bucket/data/$(date +%Y%m%d)/
```

## Cleanup

### Docker Compose

```bash
docker-compose down -v
```

### CloudFormation

```bash
aws cloudformation delete-stack --stack-name stock-prediction-infra
```

### ECS Manual Cleanup

```bash
# Delete service
aws ecs delete-service --cluster your-cluster --service your-service --force

# Delete cluster
aws ecs delete-cluster --cluster your-cluster

# Delete ECR repositories
aws ecr delete-repository --repository-name stock-prediction --force
```

## Support

For deployment issues:
1. Check logs first
2. Review AWS documentation
3. Open an issue on GitHub
4. Contact support team
