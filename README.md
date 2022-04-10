# PayNearby - part 1 - Documentation.

##### I am using Google Cloud Platform to design the entire ETL pipeline.
### There are 2 Google cloud services that are being used for this pipeline.
###       CLoud Functions.
###       Cloud SQL - MySQL service.

### Programming tools
####      Python 3.7
####      SQL

### database
####      MySQL
####      Given data is structured, I have chosen an RDBMS database - MySQL.

## Steps to recreate:-
### 1. Create a container repository:-
### build and push an image to this container repository with the below given commands:-
cd PayNearby
Docker build . -t Paynearby
docker tag paynearby container-repo-address
docer push container-repo-address

### 2. Cloud Functions:-
#### using Google Cloud to implement this, search for Cloud Functions in GCP console, 
#### hit "create Function". 
#### configure a storage bucket as trigger with object create as event.
#### while creating, change the source to container repository and refer to the image pushed back in step 1.
#### for configuring database credentials, there are 2 options.
##### 1. refer to a secret manager.
##### 2. or add the credentails as environment variables.
 
these are the variables that are required for this function to work:-

DB_HOST  - database host IP address

DB_USER  - db user name

DB_PASS  - db password

DB_NAME  - PAYNEARBY

### 3. Database:-

#### create a Database using the below name:-

CREATE DATABASE PAYNEARBY;

#### create the required tables:-

create table DIM_PINCODE(
ID VARCHAR(20) primary key,
PLACE_NAME VARCHAR(50),
ADMIN_NAME VARCHAR(50),
LATITUDE FLOAT,
LONGITUDE FLOAT,
ACCURACY INT,
LOAD_DATE datetime
);

create table STG_PINCODE(
ID VARCHAR(20),
PLACE_NAME VARCHAR(50),
ADMIN_NAME VARCHAR(50),
LATITUDE FLOAT,
LONGITUDE FLOAT,
ACCURACY INT
);

## Execution:-
#### upload the given csv files into the storage bucket.
#### The function triggers as soon as the file is uploaded to the configured bucket, the ingested file is deleted from the bucket once processed.
