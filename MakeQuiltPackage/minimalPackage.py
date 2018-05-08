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

def GenerateREADME(readmePath):
    with open(readmePath,'w') as myFile:
        myFile.write('# Package Summary')

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
            
def GetClassIDs(openImages, query):
    classDescriptionDF = openImages.class_descriptions()
    classDescriptionDF.columns = ['LabelName', 'LabelDescription']
    rowsResult = classDescriptionDF[classDescriptionDF.LabelDescription.str.match(query, flags=re.IGNORECASE)]
    return rowsResult.LabelName

def get_trianable(regex, bbox=False, dry=False, frac=1):
    """search trainable classes for matching keywords
       only return human labeled examples with a Confidence == 1
       regex: match against 'Description' of label
              (hint "^(?!.*FOO).*$" negates FOO)
       bbox: bounding box data?
       dry: stop at label match, don't build actual test/train/validation sets
    """    
    trainable = oi.classes_bbox_trainable() if bbox else oi.classes_trainable()
    descriptions = oi.class_descriptions();
    # Label column is nameless; pandas calls it "0"
    trainable_descriptions = pd.merge(trainable, descriptions, on='0', validate="1:1")
    # Give columns nice names
    trainable_descriptions.columns = ['LabelName', 'Description']
    # Get labels that match regex
    matches = trainable_descriptions[trainable_descriptions['Description'].str.match(regex, flags=re.IGNORECASE)]
    # Print number of matches, matching labels
    n_matches = len(matches)
    #print("%s label(s) matching %s" % (n_matches, regex))
    #print([m for m in matches['Description'].unique()])
    if (n_matches <= 0 or dry):
        return {}
    # generate lists of links
    data = {}
    for fold in ('train', 'test', 'validation'):
        ann = 'annotations_human_bbox' if bbox else 'annotations_human'
        # trailing () tells quilt to turn attr into a dataframe
        ids = operator.attrgetter("{}.{}".format(fold, ann))(oi)().sample(frac=frac, random_state=1)
        # filter down to high confidence
        ids = ids[ids['Confidence'] == 1]
        matching_ids = pd.merge(matches, ids, on='LabelName', validate="1:m")
        # image urls
        urls = operator.attrgetter("{}.images".format(fold, ann))(oi)()
        matching_urls = pd.merge(matching_ids, urls, on='ImageID')
        data[fold] = matching_urls
        print("{}: {} examples".format(fold, len(matching_urls)))
    return data

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