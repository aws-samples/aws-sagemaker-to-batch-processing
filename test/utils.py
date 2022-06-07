'''
####################################################################################
###### utils.py
####################################################################################
# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.  
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at  
# http://aws.amazon.com/agreement or other written agreement between Customer and either
# Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
####################################################################################
# May 2022
# Utility fn
# that uses implements standard data science data processing toolkits like
# pandas and numpy, to join datasets, prepare features and write outputs
####################################################################################
'''

import os
import time

def mkpath_if_not_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)

def log_time_taken(from_time, message='', units='secs'):
    time_taken = time.time()-from_time
    if units=='mins':
        time_taken/=60
    print(f'Time taken for {message} = {time_taken:.2f} {units}')
    return time.time()