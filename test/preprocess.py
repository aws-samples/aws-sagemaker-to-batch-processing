'''
####################################################################################
###### preprocess.py
####################################################################################
# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.  
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at  
# http://aws.amazon.com/agreement or other written agreement between Customer and either
# Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
####################################################################################
# May 2022
# Preprocess fn
# that uses implements standard train/test split fn to prepare
# train, test and validation files
####################################################################################
'''
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import utils

SEED=0

def print_df_shape(df, df_name='data'):
    print(f"Shape of {df_name} is:", df.shape)

def read_input_data(input_data_folder):
    input_data_path = os.path.join(input_data_folder, "dataset.csv")
    df = pd.read_csv(input_data_path)
    print_df_shape(df)
    return df

def run_sklearn_train_test_split(df, test_size):
    train, test = train_test_split(df, test_size=test_size)
    print_df_shape(train, df_name='train set')
    print_df_shape(test, df_name='test set')
    return train, test

def get_train_set_metrics(df_train):
    num_rows=df_train.shape[0]
    num_features=df_train.shape[1]
    avg_age = df_train['age'].mean()
    num_classes = df_train['class of worker'].unique().shape[0]
    metrics = [[num_rows, num_features, avg_age, num_classes]]
    df_metrics = pd.DataFrame(metrics, columns=['num_rows','num_feats','avg_age','num_classes'])
    return df_metrics

def create_output_dirs(output_data_folder):
    try:
        utils.mkpath_if_not_exist(output_data_folder)
        print(f"Successfully created directory {output_data_folder}")
    except Exception as e:
        # if the Processing call already creates these directories (or directory otherwise cannot be created)
        print(e)
        print("Could not create directory")
        pass

def save_output_files(df, 
    output_data_folder, 
    file_name='train.csv'
    ):
    try:
        df.to_csv(f"{output_data_folder}/{file_name}")
        print(f"Wrote {file_name} files successfully to {output_data_folder}")
    except Exception as e:
        print("Failed to write the files")
        print(e)
        pass
