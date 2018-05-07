import quilt
import pandas as pd
import os
import shutil
import pathlib

############################################
def GenerateREADME(readmePath):
	with open(readmePath,'w') as myFile:
		myFile.write('# Package Summary')

def GeneratePandaTable(imageIDList, annotationDF, metadataPath):
	#imageIDList is a python list
	rowsResult = pd.DataFrame(data = {'ImageID' : imageIDList})
	metadata = pd.merge(rowsResult, annotationDF)
	metadata.to_csv(metadataPath)

#########################

dataFolder = './minPackage'
imageIDList = ['b91d35b5b1e21b3a', 'b91e1150fafff17c', 'b91f356627cc68b1']

GenerateREADME(dataFolder+'/README.md')
from quilt.data.examples import openimages as oi
annotationDF = oi.train.annotations_human()
GeneratePandaTable(imageIDList, annotationDF, dataFolder + '/PandaTable.csv')


if (os.path.exists(dataFolder+'/build.yml')):
	os.remove(dataFolder+'/build.yml')

quilt.generate(dataFolder)
quilt.build("ykarbaschi/minimalPackage", dataFolder+'/build.yml')

from quilt.data.ykarbaschi import minimalPackage
minimalPackage._meta['trainable'] = True
minimalPackage._meta['bbox'] = True
minimalPackage._meta['labelName'] = 'Minimal Package'
minimalPackage._meta['image_count'] = 3

for imageID in imageIDList:
	imageDataNode = getattr(getattr(minimalPackage, 'images'), imageID)
	try:
		imageDataNode._meta['bbox'] = pd.DataFrame(data=['for example bbox information'])
	except Exception as e:
		pass

quilt.login()
quilt.build("ykarbaschi/minimalPackage", minimalPackage)
quilt.push("ykarbaschi/minimalPackage", is_public=True)
