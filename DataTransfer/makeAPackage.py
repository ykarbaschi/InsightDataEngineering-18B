import quilt
from quilt.data.examples import openimages as oi
import pandas as pd
import os
import shutil
import pathlib

############################################

def ProcessQuery(classDescriptionDF, annotationDF, query):
	#query is a regex
	# second column should be descriptions 'label'
	classDescriptionDF.columns = ['LabelName', 'LabelDescription']
	classDescriptionDF['descLower'] = classDescriptionDF.LabelDescription.str.lower()
	rowsResult = classDescriptionDF[classDescriptionDF.descLower.str.contains(query, regex=True)]

	metadata = pd.merge(rowsResult, annotationDF)
	return metadata.ImageID.tolist(), metadata

def CopyImages(IDs, source, dest):
	for id in IDs:
		full_file_name = ''
		for src in source:
			#find the location of file
			if (os.path.isfile(os.path.join(src, id))):
				full_file_name = os.path.join(src, id)
				break

		if full_file_name == '':
			with open('logPath','+') as myFile:
					myFile.write('this file couldnt be found {}\n'.format(id))
			continue


		if (not os.path.exists(dest+id)):
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
tempDest = '/data3TB/quiltPackage/police_car/images/'
packageSRC = '/data3TB/quiltPackage/police_car/'
logPath = 'data3TB/quiltPackage/copyPoliceCar.out'
query = 'police car'
#final dest is Quilt servers

pathlib.Path(tempDest).mkdir(parents=True, exist_ok=True)
# go and find image IDs related to this queyr
imageIDsList, metadata = ProcessQuery(classDescriptionDF, annotationDF, query)
# list of Image IDs
CopyImages(imageIDsList, dataSource, tempDest)

quilt.generate(packageSRC)

quilt.build("ykarbaschi/police_car", packageSRC+'build.yml')

from quilt.data.ykarbaschi import police_car

#police_car._set(['metadata'], metadata)
police_car._meta['imageMetadata'] = metadata

#all_bbox = oi.train.annotations_human_bbox();

for imageID in imageIDsList:
	try:
		police_car._set(['images', imageID, 'metadata'], pd.DataFrame(data=['for example bbox information']))
	except Exception as e:
		pass

quilt.login()
quilt.build("ykarbaschi/police_car", police_car)
quilt.push("ykarbaschi/police_car", is_public=True)
