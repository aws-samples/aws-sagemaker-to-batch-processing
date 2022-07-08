import pandas as pd
from multiprocessing import Pool
import multiprocessing
import psutil
import os
import shutil
import math
import time
import gc
from functools import partial
import glob

def normalizing_wage_at_row_level(row, df):
    if row[6] == 0:
        impute_wage = df.groupby(['sex','class of worker', 'race'])['wage per hour'].mean()
        return impute_wage[row[13]][row[2]][row[11]]
    else:
        return row[6]

def normalizing_wage(n, df_full):
    print(n)
    df = pd.read_csv(f'tmp/tmp/dfol{n}.csv')
    df['normalized_wage_per_hour'] = df.apply(normalizing_wage_at_row_level, df = df_full, axis = 1)
    df.to_csv(f'tmp/tmp2/final{n}.csv', index=False)


def multiproc_normalize_wage(ids, df):
    n_worker = psutil.cpu_count() - 1

    try:
        shutil.rmtree('tmp/tmp/')
    except FileNotFoundError:
        pass
    os.makedirs('tmp/tmp/')

    try:
        shutil.rmtree('tmp/tmp2/')
    except:
        pass
    os.makedirs('tmp/tmp2/')

    for n in range(n_worker):
        chunk_size = int(math.ceil(len(ids) / (n_worker)))
        chunk_id = ids[n * chunk_size : (n + 1) * chunk_size]

        a = df.loc[df['id'].isin(chunk_id)]
        a.to_csv(f'tmp/tmp/dfol{n}.csv', index=False)
    
    gc.collect()

    print('normalizing wage: multiprocessed')
    p = multiprocessing.Pool(processes=n_worker)
    n = [i for i in range(n_worker)]
    p.map(partial(normalizing_wage, df_full = df), n)
    time.sleep(0.5)
    p.close()
    p.join()
    
    print('compiling df_ol')
    df_ol = pd.concat([pd.read_csv(x,dtype={'id':str}) for x in glob.glob('tmp/tmp2/final*')])

    return df_ol

if __name__ == '__main__':
    df = pd.read_csv('census-income.csv')
    df['id'] = df.index + 1
    first_column = df.pop('id')
    df.insert(0, 'id', first_column)
    multiproc_normalize_wage(df['id'], df)

