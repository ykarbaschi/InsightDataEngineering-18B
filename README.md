# Google Open Image V3, Making it Accessible

## Overview
I've worked with a YCombinator company, Quilt, as a consultant for my fellowship project at Insight. Our goal was to make 18 TB of data accessible on a single machine.
* [Slides](http://bit.ly/18TB_Dataset_AtYourFingertips_slides)
* [Quilt Public Repository](https://quiltdata.com/search/?q=)

## Motivation
[Google Open Image V3](https://storage.googleapis.com/openimages/web/index.html) is a public image dataset with 18TB of data and 9 million annotated images. Image recognistion is one of the hottest topic in data sciecne and have many applications (self-driving cars, healthcare, etc). But no one builds custom dataset since data is too big. In this project I've worked with [Quilt](https://quiltdata.com/) to make this dataset accessible on smaller machines.

## Quilt Packages
Quilt is providing a functionality like Docker images or Github but for data. You can add or delete files and folders and version that. Then push it to Quilt servers and share it. Through hashing it provides deduplication of data and increase upload and download files from 5 to 20 times faster. More information on how to start working with Quilt can be found [here](https://blog.quiltdata.com/data-packages-for-fast-reproducible-python-analysis-c74b78015c7f).

## Filter 18 TB data before downloading
I've downloaded and cleaned all images in this dataset on EC2 machines. Quilt packges can be build with a single command from a folder. But without metadata the packge is not useful. Each file/folder is represented as a node in a tree-like data structure in a Quilt package. Each node can have unlimited metadata attached which make them queryable. I've extracted meatada and attached related metadata to each node so it can can filtered and accessed among 18 TB of images. Here is an example of how filtering works (Note since Quilt is actively developing new features, syntax might be different.):
```python
import quilt
from quilt.data.example import openimages as oi
police_car = oi._filter(count=100, {'subset' = 'test', 'size' <= 1MB})

```
