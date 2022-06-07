#!/bin/bash

##########################################################################
##########################################################################
##### build_sagemaker_container_for_arm64.sh
##### This script will re-build the SageMaker Sklearn docker image on a
##### ARM64 architecture. It will clone the existing x86 version of the 
##### code to build the image, replace the appropriate steps for arm64
##### and re-build this image. It will push the result to ECR
##### To run this, bash 
##### ./build_and_push_arm_image.sh
#####
##### Date: Feb 2022
##### Creator: adarsjan@amazon.com
##########################################################################
##########################################################################
set -e # stop if anything fails
##########################################################################
#### SETUP THE NAMING
SAGEMAKER_SKLEARN_VERSION=${version}-${platform}
PY_VERSION=37
COMPUTE=cpu
account=$AWS_ACCOUNT_ID
account_sklearn=121021644041
region=$AWS_DEFAULT_REGION
TAG=${SAGEMAKER_SKLEARN_VERSION}-${COMPUTE}-py${PY_VERSION}
BASE_IMAGE_NAME=sklearn-base:${TAG}
FINAL_IMAGE_NAME=preprod-sklearn:${TAG}
EXTENSION_IMAGE_NAME=preprod-sklearn-extension:${TAG}
EXTEND_RAY=false

#### FIX THE NAME FOR THE ECR IMAGE TO BE UPLOADED
BATCH_IMAGE_NAME=${IMAGE_REPO_NAME}
BATCH_IMAGE_FULLNAME=${BATCH_IMAGE_NAME}:${TAG}
ECR_IMAGE_NAME="${account}.dkr.ecr.${region}.amazonaws.com/${IMAGE_REPO_NAME}:${IMAGE_TAG}"

##########################################################################
#### BUILD base sklearn images in Docker before building the AWS batch version

if [ $platform == "arm64" ]; then
    echo "Platform $platform is equal to arm64, we will rebuild Sklearn version on this arch"
    docker build -t ${BASE_IMAGE_NAME} -f ${repo}/docker/${SAGEMAKER_SKLEARN_VERSION}/base/Dockerfile.cpu -o type=docker .
    cd ${repo}
    pip3 install wheel
    python3 setup.py bdist_wheel
    docker build -t ${FINAL_IMAGE_NAME} -f docker/${SAGEMAKER_SKLEARN_VERSION}/final/Dockerfile.cpu -o type=docker .
    docker build -t ${EXTENSION_IMAGE_NAME} -f docker/${SAGEMAKER_SKLEARN_VERSION}/extension/Dockerfile.cpu -o type=docker .
    if [ $EXTEND_RAY == "true" ]; then
        docker build -t ${EXTENSION_IMAGE_NAME} -f docker/${SAGEMAKER_SKLEARN_VERSION}/ray-extension/Dockerfile.cpu -o type=docker .
    else
        echo "Not extending Docker image for building and installing Ray from source..."
    fi
    cd ..
else
    echo "Platform $platform is not arm64, will use default AWS Sklearn version as base"
    aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${account_sklearn}.dkr.ecr.${region}.amazonaws.com
fi
##########################################################################
#### BUILD THE AWS BATCH VERSION on top of this

sleep 2
docker build -t ${BATCH_IMAGE_FULLNAME} -f ${repo}/docker/${SAGEMAKER_SKLEARN_VERSION}/aws-batch-extension/Dockerfile.cpu -o type=docker .
docker image tag ${BATCH_IMAGE_FULLNAME} ${ECR_IMAGE_NAME}

echo ${ECR_IMAGE_NAME}

