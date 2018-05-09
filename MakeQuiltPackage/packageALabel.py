import operator
import os
import pathlib
import re
import shutil
import time
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

def GenerateImageMetadata(folds, allImageIDs, Helmet, annList):
	for fold in folds:
		imageIDList = allImageIDs[fold]
		for ann in annList:
			metadata = operator.attrgetter("{}.{}".format(fold, ann))(oi)()
			for imageID in imageIDList:
				imageDataNode = getattr(getattr(Helmet, 'images'), 'n'+imageID)	
				metadataDF = metadata.loc[metadata.ImageID.str.match(imageID)]
				if metadataDF.shape[0] > 0:
					imageDataNode._meta['custom'][ann] = metadataDF

t = time.time()


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

pkgNode = quilt.load('ykarbaschi/'+classDescription)

pkgNode._meta['custom']['trainable'] = classID in oi.classes_trainable().values
pkgNode._meta['custom']['bbox'] = classID in oi.classes_bbox().values
pkgNode._meta['custom']['labelName'] = classDescription
pkgNode._meta['custom']['image_count'] = GetNumImages(folds, allImageIDs)

GenerateImageMetadata(folds, allImageIDs, pkgNode, annList)
print('Metadata generation completed')

quilt.build('ykarbaschi/'+ classDescription, pkgNode)
quilt.push('ykarbaschi/'+ classDescription, is_public=True)

elapsed = time.time() - t
print(elapsed)