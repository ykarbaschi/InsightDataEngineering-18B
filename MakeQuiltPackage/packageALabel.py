import operator
import os
import pathlib
import re
import shutil
import pandas as pd
import quilt
from quilt.data.examples import openimages as oi

def CopyImages(folds, allImageIDs, sourceFolder, destFolder, logPath):
    for fold in folds:
        IDs = allImageIDs[fold]
        source = sourceFolder + fold + '/images/'
        dest = destFolder + '/images/'
        pathlib.Path(dest).mkdir(parents=True, exist_ok=True)

        for id in IDs:
            full_file_name = None
            if (os.path.isfile(source+id)):
                full_file_name = source+id

            if not full_file_name:
                with open(logPath, 'a+') as myFile:
                        myFile.write('this file couldnt be found {}{}\n'.format(source, id))
                continue

            if (not os.path.exists(dest+id)):
                try:
                    shutil.copy(full_file_name, dest)
                except Exception as e:
                    with open(logPath, 'a+') as myFile:
                            myFile.write('this file can not be written be found {}{}\n'.format(dest,id))

def GetImageIDs(folds, classID, annList):
	allImageIDs = {}
	for fold in folds:
		ids = pd.DataFrame(data={'ImageID':[]})
		for ann in annList:
			metadata = operator.attrgetter("{}.{}".format(fold, ann))(oi)()
			filteredMetadata = metadata.loc[metadata.LabelName.str.match(classID)]
			filteredMetadata = filteredMetadata.filter(items=['ImageID'])
			ids = ids.append(filteredMetadata)

		ids = ids.drop_duplicates()
		allImageIDs[fold] = ids.ImageID

	return allImageIDs

def GenerateREADME(readmePath):
    with open(readmePath,'w') as myFile:
        myFile.write('# Package Summary')

def GetNumImages(folds, allImageIDs):
	sum = 0;
	for fold in folds:
		sum += allImageIDs[fold].size

	return sum

def GetImageMetadata(fold, ann, imageID):
	metadata = operator.attrgetter("{}.{}".format(fold, ann))(oi)()
	return metadata.loc[metadata.ImageID.str.match(imageID)]

def GenerateImageMetadata(folds, allImageIDs, Helmet, annList):
	for fold in folds:
		imageIDList = allImageIDs[fold]
		for imageID in imageIDList:
			try:
				imageDataNode = getattr(getattr(Helmet, 'images'), imageID)
			except Exception as e:
				print(e)
			
			for ann in annList:
				try:
					metadataDF = GetImageMetadata(fold, ann, imageID)
					if metadataDF.shape[0] > 0:
						imageDataNode._meta[ann] = metadataDF
				except Exception as e:
					print(e)

classID = '/m/0zvk5'
classDescription = 'Helmet'

#folds = ['test', 'train', 'validation']
folds = ['test']
annList = ['annotations_human', 'annotations_machine', 'annotations_human_bbox']
packagePath = '/data3TB/quiltPackage/'+ classDescription + '/'

pathlib.Path(packagePath).mkdir(parents=True, exist_ok=True)

allImageIDs = GetImageIDs(folds, classID, annList)
# I assumed all train data is in 16TB for now
dataSource = '/data16TB/'
logPath = packagePath + 'packageBuilding.out'

print('copy has started')
CopyImages(folds, allImageIDs, dataSource, packagePath, logPath)

GenerateREADME(packagePath+'README.md')

if (os.path.exists(packagePath+'build.yml')):
    os.remove(packagePath+'build.yml')

quilt.generate(packagePath)
quilt.build('ykarbaschi/' + classDescription, packagePath + 'build.yml')

# I dont know how to dynamically change the package name here, 
# I hard coded police_car for now
from quilt.data.ykarbaschi import Helmet

Helmet._meta['trainable'] = classID in oi.classes_trainable().values
Helmet._meta['bbox'] = classID in oi.classes_bbox().values
Helmet._meta['labelName'] = classDescription
Helmet._meta['image_count'] = GetNumImages(folds, allImageIDs)

# Helmet should be corrected
GenerateImageMetadata(folds, allImageIDs, Helmet, annList)

quilt.build('ykarbaschi/'+ classDescription, Helmet)
quilt.push('ykarbaschi/'+ classDescription, is_public=True)