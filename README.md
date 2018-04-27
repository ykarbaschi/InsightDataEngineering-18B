# InsightDataEngineering-18B

# Project Idea
Make Open Image Dataset V3 available in consumable size for data sciecntist to use as quilt packages. Main purpose of Quilt package is reproducibility of machine learning models.

# Proposal
* Download all images
  * Verify downloaded files
* Partition them into consumable and meaningful chunks (Maybe labels?)
* Make Quilt Package for each chunk
  * Consider each quilt package as a python library whcih can be imported.
  * Each quilt contains metadata table. It can be filtered before importing.

# Challenges
Downloading and Verifying Result
* I've extracted all image urls from metadata table and started a multithread download
* Download files can fail -- should keep track which is failed
* Some images deleted and instead we only have an "Image is deleted" sticker as 2k image. (tring to find a way to detect those)
