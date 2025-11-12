#!/bin/bash

# AWS ECS Deployment Script for Stock Prediction Application

set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REPO_NAME="stock-prediction"
CLUSTER_NAME="production-cluster"
SERVICE_NAME="stock-prediction-service"
TASK_DEFINITION_FAMILY="stock-prediction-task"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting deployment process...${NC}"

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo -e "${YELLOW}AWS Account ID: ${AWS_ACCOUNT_ID}${NC}"
echo -e "${YELLOW}ECR Repository: ${ECR_REPO_URI}${NC}"

# Create ECR repository if it doesn't exist
echo -e "${GREEN}Checking ECR repository...${NC}"
aws ecr describe-repositories --repository-names ${ECR_REPO_NAME} --region ${AWS_REGION} 2>/dev/null || \
    aws ecr create-repository --repository-name ${ECR_REPO_NAME} --region ${AWS_REGION}

# Login to ECR
echo -e "${GREEN}Logging in to ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO_URI}

# Build Docker image
echo -e "${GREEN}Building Docker image...${NC}"
docker build -t ${ECR_REPO_NAME}:latest .

# Tag image
echo -e "${GREEN}Tagging image...${NC}"
docker tag ${ECR_REPO_NAME}:latest ${ECR_REPO_URI}:latest
docker tag ${ECR_REPO_NAME}:latest ${ECR_REPO_URI}:$(date +%Y%m%d%H%M%S)

# Push to ECR
echo -e "${GREEN}Pushing image to ECR...${NC}"
docker push ${ECR_REPO_URI}:latest
docker push ${ECR_REPO_URI}:$(date +%Y%m%d%H%M%S)

# Update task definition
echo -e "${GREEN}Updating ECS task definition...${NC}"
TASK_DEFINITION=$(aws ecs describe-task-definition --task-definition ${TASK_DEFINITION_FAMILY} --region ${AWS_REGION})
NEW_TASK_DEF=$(echo $TASK_DEFINITION | jq --arg IMAGE "${ECR_REPO_URI}:latest" '.taskDefinition | .containerDefinitions[0].image = $IMAGE | del(.taskDefinitionArn) | del(.revision) | del(.status) | del(.requiresAttributes) | del(.compatibilities) | del(.registeredAt) | del(.registeredBy)')

# Register new task definition
echo -e "${GREEN}Registering new task definition...${NC}"
NEW_TASK_INFO=$(aws ecs register-task-definition --region ${AWS_REGION} --cli-input-json "$NEW_TASK_DEF")
NEW_REVISION=$(echo $NEW_TASK_INFO | jq '.taskDefinition.revision')

# Update service
echo -e "${GREEN}Updating ECS service...${NC}"
aws ecs update-service --cluster ${CLUSTER_NAME} \
    --service ${SERVICE_NAME} \
    --task-definition ${TASK_DEFINITION_FAMILY}:${NEW_REVISION} \
    --region ${AWS_REGION}

echo -e "${GREEN}Deployment initiated successfully!${NC}"
echo -e "${YELLOW}Monitor the deployment status in the AWS ECS console${NC}"
