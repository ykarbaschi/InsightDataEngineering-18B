import quilt
from quilt.data.examples import openimages as oi
import pandas as pd
import os
import shutil
import numpy as np
import pathlib
############################################

def ProcessQuery(classDescriptionDF, annotationDF, query):
    #query is a regex

	# second column should be descriptions 'label'
    classDescriptionDF.columns = ['LabelName', 'LabelDescription']
    classDescriptionDF['descLower'] = classDescriptionDF.LabelDescription.str.lower()
    rowsResult = classDescriptionDF[classDescriptionDF.descLower.str.contains(query, regex=True)]

    return (pd.merge(rowsResult, annotationDF)).ImageID.tolist()

def CopyImages(IDs, source, dest):
    for id in IDs:
	full_file_name = None
	for src in source:
	    #find the location of file
	    if (os.path.isfile(os.path.join(src, id))):
		full_file_name = os.path.join(src, id)
		break

	if full_file_name:
	    with open('logPath','+') as myFile:
		myFile.write('this file couldnt be found {}\n'.format(id))
	    continue

	try:
	    shutil.copy(full_file_name, dest)
	except Exception as e:
	    with open('logPath','+') as myFile:
		myFile.write('this file can not be written be found {}\n'.format(id))
#########################

# lets say for train
dataSource = ['/data16TB/train/images/', '/data3TB/train/images/']
annotationDF = oi.train.annotations_human();
classDescriptionDF = oi.class_descriptions()
tempDest = '/data3TB/quiltPackage/train/'
logPath = 'data3TB/quiltPackage/copy.out'
query = 'dog'
#final dest is Quilt servers

pathlib.Path(tempDest).mkdir(parents=True, exist_ok=True)
# go and find image IDs related to this queyr
imageIDsList = ProcessQuery(classDescriptionDF, annotationDF, query)
# list of Image IDs
CopyImages(imageIDsList, dataSource, tempDest)

