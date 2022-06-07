#!/bin/bash

################################################################
################################################################
## sagemaker_on_aws_batch.sh
## This fetch and run script will try mimic the sagemaker functions
## on aws batch
################################################################
## This dummy script will load one single data source (input_data_one)
## from S3 to the instance that is running this task
## The job itself does a simple train/test split task, and 
## calculates some metrics, and saves the output back to S3
################################################################
################################################################
## PARAMETERS
## train-test-split: float, ratio of train to test set size
## validation-flag: bool, whether or not validation set is generated
## entry-point: pls pass the s3 path of the entry point script
## env: dev or prod (default dev)
## code-bucket : bucket where code for reranking is stored 
## input-bucket: bucket where input raw data is stored 
## output-bucket : bucket where reranking intermediate data is stored
################################################################
################################################################


BASENAME="${0##*/}"
AWS_BATCH_EXIT_CODE_FILE="/tmp/batch-exit-code"
SAGEMAKER_SUBMIT_DIRECTORY=/opt/ml/code
SAGEMAKER_PROCESS_DIRECTORY=/opt/ml/processing
        
declare -a PYARGS=()

parse_args() {
    while [[ $# -gt 0 ]]; do
        key="$1"
        [[ $# -eq 1 ]] && max_shift=1 || max_shift=2
        case $key in
        -h|--help)
            echo "Usage: ${BASH_SOURCE[0]##*/} [options] -- [python script's options]"
            echo -e "  --train-test-split <ARG>"
            echo -e "  --validation-flag <ARG>"
            echo -e "  --entry-point <ARG>"
            echo -e "  --env <ARG>"
            echo -e "  --code-bucket <ARG>"
            echo -e "  --input-bucket <ARG>"
            echo -e "  --output-bucket <ARG>"
            exit 0
            ;;
        --train-test-split)
            TRAIN_TEST_SPLIT="$2"
            shift $max_shift
            ;;
        --validation-flag)
            VALIDATION_FLAG="$2"
            shift $max_shift
            ;;
        --entry-point)
            PREPROCESING_ENTRYPOINT="$2"
            shift $max_shift
            ;;
        --env)
            ENV="$2"
            shift $max_shift
            ;;
        --code-bucket)
            CODE_BUCKET="$2"
            shift $max_shift
            ;;
        --input-bucket)
            INPUT_BUCKET="$2"
            shift $max_shift
            ;;
        --output-bucket)
            OUTPUT_BUCKET="$2"
            shift $max_shift
            ;;
        --)
            shift
            PYARGS+=( "$@" )
            break
            ;;
        *)
            echo 'Unknown option:' "$1"
        esac
    done

}


parse_args "$@"

#By default set to dev env, need specific params set to run for prod
: "${TRAIN_TEST_SPLIT:=0.2}"
: "${VALIDATION_FLAG:=True}"
ENV="${ENV:-dev}"

# Input paths
S3_INPUT_ONE=s3://${INPUT_BUCKET}/data/sample/census/
INPUT_CHANNEL_ONE=${SAGEMAKER_PROCESS_DIRECTORY}/input/one
S3_INPUT_CODE=s3://${CODE_BUCKET}/code-repo/sagemaker-process-code/
INPUT_CHANNEL_CODE=${SAGEMAKER_PROCESS_DIRECTORY}/input/lib

# outputs
OUTPUT_CHANNEL_TRAIN=${SAGEMAKER_PROCESS_DIRECTORY}/output/data/train/
S3_OUTPUT_TRAIN=s3://${OUTPUT_BUCKET}/output-data/sample/census/train
OUTPUT_CHANNEL_VALIDATION=${SAGEMAKER_PROCESS_DIRECTORY}/output/data/validataion/
S3_OUTPUT_VALIDATION=s3://${OUTPUT_BUCKET}/output-data/sample/census/valdiataion
OUTPUT_CHANNEL_TEST=${SAGEMAKER_PROCESS_DIRECTORY}/output/data/test/
S3_OUTPUT_TEST=s3://${OUTPUT_BUCKET}/output-data/sample/census/test/
OUTPUT_CHANNEL_METRICS=${SAGEMAKER_PROCESS_DIRECTORY}/output/data/metrics/
S3_OUTPUT_METRICS=s3://${OUTPUT_BUCKET}/output-data/sample/census/metrics/

# ECHO Base variables
echo BASENAME=${BASENAME}
echo AWS_BATCH_EXIT_CODE_FILE=${AWS_BATCH_EXIT_CODE_FILE}
echo SAGEMAKER_SUBMIT_DIRECTORY=${SAGEMAKER_SUBMIT_DIRECTORY}
echo SAGEMAKER_PROCESS_DIRECTORY=${SAGEMAKER_PROCESS_DIRECTORY}
echo PREPROCESING_ENTRYPOINT=${PREPROCESING_ENTRYPOINT}

# ECHO env vars
echo ENV=${ENV}

# ECHO S3 bucket details
echo INPUT_BUCKET=${INPUT_BUCKET}
echo CODE_BUCKET=${CODE_BUCKET}
echo OUTPUT_BUCKET=${OUTPUT_BUCKET}

# ECHO S3 locations
echo S3_INPUT_ONE=${S3_INPUT_ONE}
echo S3_INPUT_CODE=${S3_INPUT_CODE}
echo S3_OUTPUT_TRAIN=${S3_OUTPUT_TRAIN}
echo S3_OUTPUT_VALIDATION=${S3_OUTPUT_VALIDATION}
echo S3_OUTPUT_TEST=${S3_OUTPUT_TEST}
echo S3_OUTPUT_METRICS=${S3_OUTPUT_METRICS}

# ECHO internal container paths
echo INPUT_CHANNEL_ONE=${INPUT_CHANNEL_ONE}
echo INPUT_CHANNEL_CODE=${INPUT_CHANNEL_CODE}
echo OUTPUT_CHANNEL_TRAIN=${OUTPUT_CHANNEL_TRAIN}
echo OUTPUT_CHANNEL_VALIDATION=${OUTPUT_CHANNEL_VALIDATION}
echo OUTPUT_CHANNEL_TEST=${OUTPUT_CHANNEL_TEST}
echo OUTPUT_CHANNEL_METRICS=${OUTPUT_CHANNEL_METRICS}

# ECHO Code fns
echo TRAIN_TEST_SPLIT=${TRAIN_TEST_SPLIT}
echo VALIDATION_FLAG=${VALIDATION_FLAG}

echo PYARGS=${PYARGS}

##################################################
####### FUNCTIONS
##################################################

log () {
  echo "${BASENAME} - ${1}"
}
# Standard function to print an error and exit with a failing return code
error_exit () {
  log "${BASENAME} - ${1}" >&2
  log "${2:-1}" > $AWS_BATCH_EXIT_CODE_FILE
  kill  $(cat /tmp/supervisord.pid)
}
#Download OUTPUT/ INPUT Data
copy_s3_data(){
  aws s3 cp --recursive $1 $2 || error_exit "Failed to copy data"  
}
# Fetch and run a script
fetch_and_run_python_script () {
  cd $INPUT_CHANNEL_CODE
  ENTRYPOINT="./sagemaker_entry_point.py"
  # Create a temporary file and download the script
  aws s3 cp "${PREPROCESING_ENTRYPOINT}" - > "${ENTRYPOINT}" || error_exit "Failed to download S3 Preprocessing script."

  # Make the file run with any given arguments
  python ${ENTRYPOINT} "${@}" || error_exit "Failed to execute script."
}

##################################################
####### DOWNLOAD,RUN CODE AND UPLOAD RESULTS TO S3
##################################################

cd $SAGEMAKER_SUBMIT_DIRECTORY

copy_s3_data $S3_INPUT_ONE $INPUT_CHANNEL_ONE
copy_s3_data $S3_INPUT_CODE $INPUT_CHANNEL_CODE

fetch_and_run_python_script --input-data-one ${INPUT_CHANNEL_ONE} \
--input-code ${INPUT_CHANNEL_CODE} \
--output-data-train ${OUTPUT_CHANNEL_TRAIN} \
--output-data-validation ${OUTPUT_CHANNEL_VALIDATION} \
--output-data-test ${OUTPUT_CHANNEL_TEST} \
--output-metrics ${OUTPUT_CHANNEL_METRICS} \
--train-test-split ${TRAIN_TEST_SPLIT} \
--validation-flag ${VALIDATION_FLAG}

cd $SAGEMAKER_SUBMIT_DIRECTORY

copy_s3_data $OUTPUT_CHANNEL_TRAIN $S3_OUTPUT_TRAIN
copy_s3_data $OUTPUT_CHANNEL_VALIDATION $S3_OUTPUT_VALIDATION
copy_s3_data $OUTPUT_CHANNEL_TEST $S3_OUTPUT_TEST
copy_s3_data $OUTPUT_CHANNEL_METRICS $S3_OUTPUT_METRICS
