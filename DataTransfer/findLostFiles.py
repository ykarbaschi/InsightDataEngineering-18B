import sys
import quilt
from quilt.data.examples import openimages as oi
import numpy as np
import subprocess

# first argument is the directory we're looking for our files
PATH = sys.argv[1]

########## should change for each set
imageIDs = oi.train.images()['ImageID']

allImageIDs = sorted(np.array(imageIDs))

downloadedFileNames = subprocess.check_output(['ls', PATH])
fileNames = sorted(np.array(downloadedFileNames.splitlines()))

zeroSizeFiles = subprocess.check_output(['find', PATH, '-size', '0', '-printf', '"%f\n"'])
zeroSizeFilesNames = sorted(np.array(zeroSizeFiles.splitlines()))

lostFiles = np.setdiff1d(allImageIDs, fileNames)

np.append(lostFiles, zeroSizeFilesNames)

np.save(PATH+'/lost.npy', lostFiles)

#np.savetxt(PATH+'/lost.log', lostFiles, delimiter=' ', fmt="%s")