# InsightDataEngineering-18B

# Project Idea
Designing a pipeline for collaboratively build and maintain the largest human labeled image dataset.

# What is the purpose, and most common use cases?
The purpose is to provide a platform for researcher to query and retrieve image metadata to train a custom classifier.

Consider how google translate works and ask participating for translating new words or verifying previous translation by other people. The goal is to provide the same thing for labeling images and bounding boxes inside of the images, but is open to public. Researchers can query images and download the metadata. Contributors can add images or change labels. Meaning of images can change or becomes meaningless over time! (Kids even don’t know what a floppy disk is)

# Scale of the data
World Population ~ 7.6 Billion
The number of smartphone ~ 5 Billion
1% will contribute 10 image with 3 labels  ~ 50 million * 10 * 3 (1.5 Billion labels)

# Challenges
Small number of tables (~5) but can grow tremendously
* needs partitioning

Handle arbitrary queries (multiple join)

Data Ingestion (Kafka, RabbitMQ)
* Decide about how to handle the request

Common queries (in-memory database like Redis)
Complex Queries (can handle join on big tables like Redshift)

Data storage on a distributed file system (HDFS)

Proposed architecture
![Alt text](./arch.png)
