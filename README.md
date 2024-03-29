## Scikit-learn ML processing jobs on AWS Graviton instances with AWS Batch

This repo contains a simple way to extend the default SageMaker container for SKLearn to be run via AWS Batch. This could be useful for those looking to leverage the power of Graviton2 instances, which are currently not available for SageMaker instances. Graviton2, run on arm64 arch, can offer significant cost efficiencies compared to x86 arch based instances. Specifically, this demo uses the c6g instances to run a data processing task, typically compute intensive. 

## Getting started

To get started with using this demo, please follow the steps below. Note that these steps are guidence, and we expect experts on SageMaker use to modify it for their use-case.

1. Clone this repo locally and navigate to the repo directory from your terminal
2. Create a new S3 bucket in your AWS Account
3. Copy the builder code to the S3 bucket (replace BUCKET_NAME with the name of your S3 bucket):
```shell
aws s3 cp --recursive codebuild/ s3://BUCKET_NAME/sagemaker-container/codebuild/
```

4. Copy the lambda invoke fn code to S3 (replace BUCKET_NAME with the name of your S3 bucket):
```shell
aws s3 cp test/lambda_function.zip s3://BUCKET_NAME/code-repo/lambda/lambda_function.zip
```
5. Run this CloudFormation template in the repo (path to template: cfn/infrastructure.yaml)

[Launch CloudFormation](https://console.aws.amazon.com/cloudformation/home?region=ap-southeast-1#/stacks/new?stackName=codebuild-sklearn-aws-batch&templateURL=https://github.com/aws-samples/aws-sagemaker-to-batch-processing/blob/main/cfn/infrastructure.yaml)

6. Fill in the values according to the defaults suggested, or change it to your own. Do note that you need to specify the architecture under which you want to build the Batch proces (Arm64 or x86), and choose instance types appropriately.
- [ ] DesiredVCPU = 1
- [ ] ImbCodeBucket = Bucket created
- [ ] ImbECRRepo = Give it a recognizable name
- [ ] ImbSklearnVersion = tested on 1.0-1 (latest as of Apr 2022)
- [ ] MaxVCPU = 128
- [ ] LambdaS3Bucket = Same Bucket created
- [ ] LambdaS3Key = If default, pass this 'code-repo/lambda/lambda_function.zip'
- [ ] Owner = AWS (just some generic tags)
- [ ] SystemName = AWS-Batch (generic tag)

7. Create a SageMaker Notebook Instance, setting instance size to ml.t2.medium.
8. Remember to set the sklearn version to 1.0-1 (which is the latest release as of writing) and py_version to p37.
9. Run the test notebooks under ./test folder. The setup comes with a dummy dataset consisting of 199523 rows and 44 columns of training data, and preprocessing steps to illustrate the point, but is not the typical case where this solution will be useful. For more details on that, see next section
- For 01_Test:
    - Replace the bucket variable with the name of the S3 bucket created
    - For the role variable, create a new IAM role with S3FullAccess and SageMakerFullAccess. Copy the ARN for the role into the variable
    - When running the SageMaker Processing Job with sklearn version 1.0-1, update the SDK version with "pip install -U sagemaker" if this error occurs: ![update-sdk-version](./docs/screenshots/update-sdk-version.png)
    - Running the SageMaker Processing Job should take about 5mins, with the preprocessing taking about 14s

- For 02_Test:
    - Replace the bucket variable with the name of the S3 bucket created
    - Include AWSBatchFullAccess in the IAM role on the AWS Console
    - Run CodeBuild in the AWS Console: CodeBuild > Build Projects > aws-dev-sklearn-aws-batch-codebuild-arm64 > Start Build
    - After running the AWS Batch Job in the notebook, check AWS Batch in the Console to ensure that the batch job succeeded. The preprocessing should take around 14s


## Typical use case
The typical use case where this solution could be useful would be in case of complicated data processing tasks done on shared memory machines.

### Current use case
The current setup includes a row-level operation to calculate a normalized wage, according to the demographics of the person (i.e. by 'sex', 'class of worker', 'race'). This function is included in the row_function_multiproc.py file to implement multi-core processing.

## Contributing
Open to contributions and improvements. This project would become obselete when SageMaker starts offering native support for ARM64 arch.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

## Authors and acknowledgment

This project was developed on the back of a ProServe customer engagement in Malaysia. We would like to thank Richard Wade, Praveen Dixit, Mehaboob Basha, Hari Krishnan and Mercy Dany for their contributions to this project.

For support on this, please contact the authors Adarsh Janakiraman (adarsjan@amazon.com) and Farhan Angullia (angullia@amazon.com)