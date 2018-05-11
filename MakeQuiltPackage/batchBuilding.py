import os
import sys
import quilt
from quilt.data.examples import openimages as oi

numPackage = sys.argv[1]
sampleClasses = oi.classes().sample(n=int(numPackage))
classes = oi.class_descriptions()

scriptName = 'pkgALabel.py'
sourcePath = '/data16TB/'
pkgPath = '/data3TB/quiltPackage/'
userID = 'ykarbaschi'
logFile = '/data3TB/quiltPackage/stats.log'
invalidImageIDsPath = '/home/ubuntu/invalidImageIDs.pickle'
for classID in sampleClasses['0'].values:

	row = classes.loc[classes['0'].str.match(classID)]
	className = str(row['1'].values[0]).lower().replace(' ', '_').replace('\'', '').replace('-','_')

	# os.system('nohup python {} {} {} {} {} {} {} > {}{}_nohup.out &'.\
	# 	format(scriptName, classID, sourcePath, pkgPath, userID, logFile, invalidImageIDsPath, pkgPath, className))

	os.system('python {} {} {} {} {} {} {}'.format(\
		scriptName, classID, sourcePath, pkgPath, userID, logFile, invalidImageIDsPath))


	print('done class {}'.format(className))