'''
####################################################################################
###### sagemaker_process_entry_point.py
####################################################################################
# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.  
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at  
# http://aws.amazon.com/agreement or other written agreement between Customer and either
# Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
####################################################################################
# May 2022
# This is the entry point for a generic pre/post processing script
# that uses implements standard data science data processing toolkits like
# pandas and numpy, to join datasets, prepare features and write outputs
# This script is designed to feed as an entry point to a SageMaker Processing
# job (or an equivalent job), and follows the conventions required for that 
# job - including the input/output folder naming consistency.
####################################################################################
'''
import argparse
import warnings
import time
import sys
import subprocess
import os
from datetime import datetime, timedelta
import glob
from pathlib import Path
import pandas as pd

warnings.filterwarnings("ignore")

def add_custom_code_to_sys_path(input_code):
    sys.path.append(input_code)

def install(package='imbalanced-learn'):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def run_data_processing(input_data_one,
                        output_data_train,
                        output_data_validation,
                        output_data_test,
                        output_metrics,
                        train_test_split,
                        switch_validation_flag,
                        ):           
    '''
    To run the data pre/post process 
    ::input_data_one : data input #1
    ::output_data_train/validation/test : Folder where final train/valid/test set will be saved
    ::output_metrics : Folder where any intermediate metrics writen from this process will be saved
    ::train_test_split : Train test split ratio
    ::switch_validation_flag : Controls whether or not to generate validation dataset
    '''
    import utils
    import preprocess
    
    inital_start_time = time.time()
    
    # LOAD the FILES
    df = preprocess.read_input_data(input_data_one)
    
    # Train test split
    train, test= preprocess.run_sklearn_train_test_split(df, test_size=train_test_split)
    if switch_validation_flag:
        train, validation= preprocess.run_sklearn_train_test_split(train, test_size=train_test_split)

    # Caclulate metrics
    df_train_metrics=preprocess.get_train_set_metrics(train)
    
    # Create the output folders
    preprocess.create_output_dirs(output_data_folder=output_data_train)
    preprocess.create_output_dirs(output_data_folder=output_data_validation)
    preprocess.create_output_dirs(output_data_folder=output_data_test)
    preprocess.create_output_dirs(output_data_folder=output_metrics)

    # Save files to output folders
    preprocess.save_output_files(df=train, 
                                output_data_folder=output_data_train,
                                file_name='train.csv',)
    preprocess.save_output_files(df=validation, 
                                output_data_folder=output_data_validation,
                                file_name='validation.csv',)
    preprocess.save_output_files(df=test, 
                                output_data_folder=output_data_test,
                                file_name='test.csv',)
    preprocess.save_output_files(df=df_train_metrics, 
                                output_data_folder=output_metrics,
                                file_name='preprocess_metrics.csv',)
    
    _=utils.log_time_taken(from_time=inital_start_time,message='Preprocessing completed', units='secs')



def parse_arg():
    parser = argparse.ArgumentParser()
    # Input params
    parser.add_argument("--input-data-one", type=str, default='/opt/ml/processing/input/one')
    parser.add_argument("--input-code", type=str, default='/opt/ml/processing/input/lib')
    parser.add_argument("--output-data-train", type=str, default=Path('/opt/ml/processing/output/data/train'))
    parser.add_argument("--output-data-validation", type=str, default=Path('/opt/ml/processing/output/data/validation'))
    parser.add_argument("--output-data-test", type=str, default=Path('/opt/ml/processing/output/data/test'))
    parser.add_argument("--output-metrics", type=str, default=Path('/opt/ml/processing/output/metrics/'))
    parser.add_argument("--train-test-split", type=float, default=0.2)
    parser.add_argument("--validation-flag", action="store_true")
    
    args, _ = parser.parse_known_args()
    print(f"Received arguments {args}")
    return args

if __name__ == "__main__":
    args = parse_arg()
    
    add_custom_code_to_sys_path(args.input_code)
    for additional_packages in ['annoy==1.17.0']:
        install(additional_packages)
        
    run_data_processing(input_data_one=args.input_data_one,
                        output_data_train=args.output_data_train,
                        output_data_validation=args.output_data_validation,
                        output_data_test=args.output_data_test,
                        output_metrics=args.output_metrics,
                        train_test_split=args.train_test_split,
                        switch_validation_flag=args.validation_flag,
                        )