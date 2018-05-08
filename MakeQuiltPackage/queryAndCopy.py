import operator
import os
import pathlib
import re
import shutil
import pandas as pd
import quilt
from quilt.data.examples import openimages as oi

def GetImageIDs(folds, query):
    #query is a regex
    # second column should be descriptions 'label'
    classDescriptionDF = oi.class_descriptions()
    classDescriptionDF.columns = ['LabelName', 'LabelDescription']
    rowsResult = classDescriptionDF[classDescriptionDF.LabelDescription.str.contains(query, regex=True,flags=re.IGNORECASE)]
    allImageIDs = {}
    for fold in folds:
        ids = operator.attrgetter("{}.{}".format(fold, 'annotations_human'))(oi)().merge(rowsResult)
        allImageIDs[fold] = ids.ImageID
    
    return allImageIDs

def GeneratePandasTable(folds, allImageIDs, imageDest):
    pandaTables = ['annotations_human', 'annotations_human_bbox', 'annotations_machine','images']
    for fold in folds:
        for ann in pandaTables:
            metadata = operator.attrgetter("{}.{}".format(fold, ann))(oi)()
            foldImageIDs = allImageIDs[fold]
            foldMetadata = pd.merge(metadata, pd.DataFrame(data={'ImageID':foldImageIDs}))
            metadataPath = imageDest + fold + '/' + ann + '.csv'
            try:
                foldMetadata.to_csv(metadataPath)
            except Exception as e:
                print(metadataPath + ' cannot be written')
            
def CopyImages(folds, allImageIDs, sourceFolder, destFolder, logPath):
    for fold in folds:
        IDs = allImageIDs[fold]
        source = sourceFolder + fold + '/images/'
        dest = destFolder + fold + '/images/'

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

def MakeFolders(dest, folds):
    for fold in folds:
        path = dest + fold + '/images'
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

folds = ['test', 'train', 'validation']
packageName = 'police_car'
imageDest = '/data3TB/quiltPackage/'+ packageName + '/'

MakeFolders(imageDest, folds)

query = 'police car' 
allImageIDs = GetImageIDs(folds, query)
# I assumed all train data is in 16TB for now
dataSource = '/data16TB/'
logPath = imageDest + 'PackageBuilding.out'
CopyImages(folds, allImageIDs, dataSource, imageDest, logPath)

GeneratePandasTable(folds, allImageIDs, imageDest)