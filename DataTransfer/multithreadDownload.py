from multiprocessing import Parallel
from urllib.request import urlretrieve
import os
import pathlib
import quilt
from quilt.data.examples import openimages as oi
import numpy as np

def parallelize(data, func):
    data_split = np.array_split(data, 10)
    pool = Pool(10)
    pool.map(func, data_split)
    pool.close()
    pool.join()

def download(DF):
    base = "/data16TB/train/images/"
    base2 = "/data3TB/train/images/"
    for index, rows in DF.iterrows():
        diskStat = os.statvfs(base)
        freeSpace = diskStat.f_bsize * diskStat.f_bfree
        id = rows['ImageID']
        url = rows['OriginalURL']
        
        if freeSpace > minDiskSpace:
            fpath = base + id
        else:
            fpath = base2 + id

        if (not os.path.exists(fpath)):
            try:
                urlretrieve(url, fpath)
            except Exception as e:
                print(e)
                print('problem: {} {}'.format(url, id))
                continue

if __name__ == '__main__':
    minDiskSpace = 1000000 #kb means ~1GB
    
    #pathlib.Path(base).mkdir(parents=True, exist_ok=True)
    
    DF = oi.train.images._data()

    parallelize(DF, download)
    