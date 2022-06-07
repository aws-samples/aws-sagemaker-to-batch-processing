####################################################################################
# This sample, non-production-ready template describes an Amazon EC2 instance and an Elastic Load Balancer.  
# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.  
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at  
# http://aws.amazon.com/agreement or other written agreement between Customer and either
# Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
####################################################################################
######################################################################
###### mxs-aa-dev-process-reranking-awsbatch-trgr.py
###### Feb 2022
###### Lambda fn for reranking using aws batch
######################################################################
#Data science
import json

# sagemaker
import boto3

#python
import os
import sys
import importlib
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import glob
import csv

print('Loading function')

batch = boto3.client('batch')

def create_unique_job_name(base_job_name, max_length=60):
    import uuid
    from datetime import datetime
    datetime_uuid=datetime.strftime(datetime.now(), "%Y%m%d%H%S")
    return f'{base_job_name}-{datetime_uuid}'[:max_length]

def get_account_details():
    account = boto3.client('sts').get_caller_identity().get('Account')
    region = boto3.session.Session().region_name
    env= 'dev' if account =='643551339491' else 'prod'
    
    return account,region,env

def run_process_job(train_test_split,
                    validation_flag,
                   ):
    account,region,env = get_account_details()
    INPUT_BUCKET= 'sagemaker-on-aws-batch-643551339491-ap-southeast-1'
    CODE_BUCKET ='sagemaker-on-aws-batch-643551339491-ap-southeast-1'
    OUTPUT_BUCKET = 'sagemaker-on-aws-batch-643551339491-ap-southeast-1'
    PREPROCESING_ENTRYPOINT = f"s3://{CODE_BUCKET}/code-repo/sagemaker-process-code/sagemaker_entry_point.py"

    #AWS BATCH PARAMETERS
    job_name=create_unique_job_name(base_job_name=f'data-process-aws-batch-run'.replace('_','-'),max_length=60)
    batch_platform=os.environ['platform'] if len(os.environ['platform'])>0 else 'arm64'
    
    #ARM 64 JOB QUEUE
    job_queue=f'arn:aws:batch:{region}:{account}:job-queue/aws-{env}-aws-batch-{batch_platform}-job-queue'
    job_definition=f'arn:aws:batch:{region}:{account}:job-definition/aws-{env}-aws-batch-{batch_platform}-job-definition'
    
    parameters = {
    'train-test-split' : train_test_split,
    'validataion-flag' : validation_flag,
    'env': env,
    'entry-point': PREPROCESING_ENTRYPOINT,
    'input-bucket': INPUT_BUCKET,
    'output-bucket': OUTPUT_BUCKET,
    'code-bucket': CODE_BUCKET,
    }

    try:
        # Submit a Batch Job
        response = batch.submit_job(jobQueue=job_queue, 
                                    jobName=job_name,
                                    jobDefinition=job_definition, 
                                    parameters=parameters)
        # Log response from AWS Batch
        print(f"Job submitted for jobName={job_name} for parameters={parameters}, Response: " + json.dumps(response, indent=2))
        # Return the jobId
        jobId = response['jobId']
        return jobId
    except Exception as e:
        print(e)
        message = f'Error submitting Batch Job for jobName={job_name} for parameters={parameters}'
        print(message)
        raise Exception(message)

def lambda_handler(event, context):
    print(f'EVENTS which triggered the job: {event}')
    
    job_id = run_process_job(train_test_split="0.2",
                             validation_flag="True"
                            )
    return {
        'statusCode': 200,
        'body': json.dumps('Lambda handler used to trigger AWS Batch jobs successfully!')
    }