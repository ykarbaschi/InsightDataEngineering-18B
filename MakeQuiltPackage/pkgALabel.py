import operator
import os
import pathlib
import pickle
import re
import shutil
import subprocess
import sys
import time
import pandas as pd
import quilt
from quilt.data.examples import openimages as oi

def CopyImages(folds, allImageIDs, sourceFolder, destFolder, logPath, imagePrefix):
	# This is only becasue train images could fit in one volumes
	trainSecSource = '/data3TB/train/images/'

	for fold in folds:
		IDs = allImageIDs[fold]
		source = sourceFolder + fold + '/images/'
		dest = destFolder + '/images/'
		pathlib.Path(dest).mkdir(parents=True, exist_ok=True)

		for id in IDs:
			newFileName = dest + imagePrefix + id
			full_file_name = None
			if fold == 'train' and \
			(os.path.isfile(source+id) or os.path.isfile(trainSecSource+id)):
				full_file_name = source+id
			elif (os.path.isfile(source+id)):
				full_file_name = source+id

			if not full_file_name:
				with open(logPath, 'a+') as myFile:
					myFile.write('this file couldnt be found {}{}\n'.format(source, id))
				continue

			if (not os.path.exists(newFileName)):
				try:
					shutil.copy(full_file_name, newFileName)
				except Exception as e:
					with open(logPath, 'a+') as myFile:
							myFile.write('this file can not be written to {}\n'.format(newFileName))

def GetImageIDs(folds, classID, annList, dataSource, invalidIDsDict):
	allImageIDs = {}
	for fold in folds:
		ids = pd.DataFrame(data={'ImageID':[]})
		#invalidIDList = GetInvalidImageIDs(dataSource+fold+'/images/', sizeThreshold)

		for ann in annList:
			metadata = operator.attrgetter("{}.{}".format(fold, ann))(oi)()
			filteredMetadata = metadata.loc[metadata.LabelName.str.match(classID)]
			filteredMetadata = filteredMetadata.filter(items=['ImageID'])
			ids = ids.append(filteredMetadata)

		ids = ids.drop_duplicates()
		invalidIDList = invalidIDsDict[fold]
		ids = ids[~ids.ImageID.isin(invalidIDList)]
		allImageIDs[fold] = ids.ImageID

	return allImageIDs

def GenerateREADME(readmePath, classDescription):
	className = classDescription.replace('_',' ').title()
	with open(readmePath,'w') as myFile:
		myFile.write('# {} from Open Images Dataset V3\nThis package is made for **{}** label description, one of the 19,794 labels in [Open Image Dataset V3](https://storage.googleapis.com/openimages/web/index.html).\n\n## Structure\n* **images** folder contains images related to this label.\n* The number of images can be derived from package node metadata like **pkgName._meta[\'custom\'][\'image_count\']**.\n* Image files and data nodes for images are prefixed with **i** but **ImageID** field in metadata tables are like Open Image Dataset.\n All image metadata such as url, author, license, etc is attached to data nodes.\n Each image metadata has a field **Subset** with a value of test, train or validation.\n* Each data node has a \'custom\' key which contain all metadata. For example for image ID **12345**, image data node is **i12345** and its metadata can be accessed via **pkgName.images.i12345._meta[\'custom\']**.\n* **annotations_human**, **annotations_machine**, **annotations_human_bbox** contains all metadata for images which are also attached to images but kept here for reference.\n* During preparing for this package, we downloaded all images with their original urls. We removed metadata information for images which were deleted from the server.'.format(className, className))

def GetNumImages(folds, allImageIDs):
	sum = 0;
	for fold in folds:
		sum += allImageIDs[fold].size

	return sum

def GetPkgSize(pkgPath):
	sizes = str(subprocess.check_output(['find', pkgPath, '-type', 'f', '-printf', '%s ']))
	sizes = sizes.split()
	del sizes[-1]
	sizes[0] = sizes[0].split('\'')[1]
	sizes = list(map(int, sizes))
	return sum(sizes)

def GenerateImageMetadata(folds, allImageIDs, pkgName, annList, logPath, imagePrefix):
	for fold in folds:
		# all image ids for this fold
		imageIDList = allImageIDs[fold]

		# only for monitoring
		imageIDSize = len(imageIDList)

		# all image information for this fold
		imageMetadata = operator.attrgetter("{}.{}".format(fold, 'images'))(oi)()
		for ann in annList:
			metadata = operator.attrgetter("{}.{}".format(fold, ann))(oi)()
			metadataAnnAllImagesThisFold = metadata[metadata.ImageID.isin(imageIDList)]
			imageMetadataAllImagesFold = imageMetadata[imageMetadata.ImageID.isin(imageIDList)]

			imageCounter = 0
			for imageID in imageIDList:
				try:
					imageDataNode = getattr(getattr(pkgName, 'images'), imagePrefix+imageID)
				except Exception as e:
					with open(logPath, 'a+') as myFile:
						myFile.write('Group node does not have image, error from invalid image or copy image {}\n'.format('n'+imageID))
					continue
				
				metadataDF = metadataAnnAllImagesThisFold.loc[metadataAnnAllImagesThisFold.ImageID.str.match(imageID)]

				# add bbox to metadata
				if ann == 'annotations_human_bbox':
					imageDataNode._meta['bbox'] = imageID in metadataAnnAllImagesThisFold.ImageID.values

				if metadataDF.shape[0] > 0:
					imageDataNode._meta[ann] = metadataDF.drop(columns=['ImageID']).to_json(orient='records')

				imageDataRow = imageMetadataAllImagesFold.loc[imageMetadataAllImagesFold.ImageID.str.match(imageID)]
				#imageDataRow = imageMetadataAllImagesFold.query('ImageID == @imageID')
				
				if imageDataRow.shape[0] != 1:
					with open(logPath, 'a+') as myFile:
						myFile.write('there should be one record for this image: {}/{}\n'.format(fold, imageID))
					continue

				for column in imageDataRow.columns:
					imageDataNode._meta[column] = str(imageDataRow[column].values[0])

				# #for monitoring
				# imageCounter = imageCounter + 1
				# if fold=='train':
				# 	print('{} of {} metadata generated for {} fold\n'.format(imageCounter, imageIDSize, fold))
			print('metadata generated for {} fold\n'.format(fold))

def GetClassDescription(classID):
	classes = oi.class_descriptions()
	row = classes.loc[classes['0'].str.match(classID)]
	return str(row['1'].values[0]).lower().replace(' ', '_')

def FilterAndSavePandasTable(folds, allImageIDs, annList, packagePath, logPath):
	# I had to get schema of pandas table before iterating on all
	pandasDF = {}
	for ann in annList:
		for fold in folds:
			metadata = operator.attrgetter("{}.{}".format(fold, ann))(oi)()
			foldImageIDs = allImageIDs[fold]
			foldMetadata = pd.merge(metadata, pd.DataFrame(data={'ImageID':foldImageIDs}))
			if ann in pandasDF:
				annDF = pandasDF[ann]
				annDF.append(foldMetadata)
				pandasDF[ann] = annDF
			else:
				pandasDF[ann] = foldMetadata

		metadataPath = packagePath + ann + '.csv'
		try:
			pandasDF[ann].to_csv(metadataPath)
		except Exception as e:
			with open(logPath, 'a+') as myFile:
				myFile.write('problem writing DataFrame {}\n'.format(ann))

def GetInvalidImageIDs(path,size):
	smallFiles = str(subprocess.check_output(['find', path, '-type', 'f', '-size', '-'+str(size)+'k', '-printf', '%f ']))
	smallImageIDs = smallFiles.split()
	del smallImageIDs[-1]
	smallImageIDs[0] = smallImageIDs[0].split('\'')[1]

	return smallImageIDs
	# we filter images based on size
''' we need to provide 5 things, LabelID,
 data source folder, package save path,
 and quilt user Id, and stats.log path
'''
# images less than this will be ignored
sizeThreshold = 4 # in KB

# for consistency file names and datanodes. avoid build to add 'n'
imagePrefix = 'i'
#classID = '/m/02x8cch'
classID = sys.argv[1]
classDescription = GetClassDescription(classID)
# dataSource = '/data16TB/'
dataSource = sys.argv[2]
# savePath = '/data3TB/quiltPackage/'
savePath = sys.argv[3]

quiltUser = sys.argv[4]
# statsPath = '/data3TB/quiltPackage/stats.log'
statsPath = sys.argv[5]
# invalidImagePath = it should be a dict with test/train/validation key and a list values
invalidImagePath = sys.argv[6]

folds = ['test','validation','train']
#folds = ['test', 'validation']
annList = ['annotations_human', 'annotations_machine', 'annotations_human_bbox']
packagePath = savePath + classDescription + '/'

pathlib.Path(packagePath).mkdir(parents=True, exist_ok=True)

invalidIDsDict = pickle.load(open(invalidImagePath, 'rb'))
allImageIDs = GetImageIDs(folds, classID, annList, dataSource, invalidIDsDict)
# I assumed all train data is in 16TB for now
logPath = savePath + 'pkgBuilding_' + classDescription + '.out'

t = time.time()
CopyImages(folds, allImageIDs, dataSource, packagePath, logPath, imagePrefix)
copyTime = time.time() - t

print('########Copy Completed#########')

FilterAndSavePandasTable(folds, allImageIDs, annList, packagePath, logPath)
print('######## Panda Table Generated#########')

GenerateREADME(packagePath+'README.md', classDescription)
if (os.path.exists(packagePath+'build.yml')):
	os.remove(packagePath+'build.yml')

t = time.time()
quilt.generate(packagePath)
quilt.build(quiltUser + '/' + classDescription, packagePath + 'build.yml')

pkgNode = quilt.load(quiltUser + '/' +classDescription)

pkgNode._meta['trainable'] = classID in oi.classes_trainable().values
pkgNode._meta['labelName'] = classDescription
numImages = GetNumImages(folds, allImageIDs)
pkgNode._meta['image_count'] = numImages

GenerateImageMetadata(folds, allImageIDs, pkgNode, annList, logPath, imagePrefix)
print('######## Image Metadata Generated#########')

quilt.build(quiltUser + '/' + classDescription, pkgNode)
print('######## New Package Generated#########')

buildPkgTime = time.time()-t

t = time.time()
quilt.push(quiltUser+ '/' + classDescription, is_public=True)
pushTime = time.time()-t

pkgSize = GetPkgSize(packagePath)

with open(statsPath, 'a+') as myFile:
	myFile.write('{} {} {} {} {} {}\n'.format(classDescription, numImages, pkgSize, copyTime, buildPkgTime, pushTime))

#cleaning
quilt.rm(quiltUser+ '/' + classDescription, force=True)
shutil.rmtree(packagePath)
