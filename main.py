
# importing required libraries
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine, types
import os
from google.cloud import storage

def delete_file(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()
    print(f"file {blob_name} deleted.")

def ETL(cursorObject):
    try:
        queries =   [
                    '''INSERT INTO DIM_PINCODE (ID, PLACE_NAME, ADMIN_NAME, LATITUDE, LONGITUDE, ACCURACY, LOAD_DATE)
                        SELECT stg.ID, stg.PLACE_NAME, stg.ADMIN_NAME, stg.LATITUDE, stg.LONGITUDE, stg.ACCURACY, now()
                        FROM STG_PINCODE stg
                        ON DUPLICATE KEY UPDATE
                        PLACE_NAME = stg.PLACE_NAME, 
                        ADMIN_NAME = stg.ADMIN_NAME, 
                        LATITUDE = stg.LATITUDE, 
                        LONGITUDE = stg.LONGITUDE, 
                        ACCURACY = stg.ACCURACY,
                        LOAD_DATE = now()
                    '''
                    ]
        for statement in queries:
            cursorObject.execute(statement)
    except Exception as e:
        raise ValueError(str(e))

def QA(cursorObject):
    try:
        testcases = [
                    'select * from STG_PINCODE stg where not exists (select * from DIM_PINCODE dim where dim.ID = stg.ID)',
                    ]
        for testcase in testcases:
            cursorObject.execute(testcase)
            cursorObject.fetchall()
            number_of_rows = cursorObject.rowcount
            if number_of_rows != 0:
                raise ValueError("Could not update all records from staging to target, please check your ETL process")
    except Exception as e:
        raise ValueError(str(e))

def main(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
    event (dict): Event payload.
    context (google.cloud.functions.Context): Metadata for the event.
    """
    try:
        db_user = os.environ["DB_USER"]
        db_pass = os.environ["DB_PASS"]
        db_name = os.environ["DB_NAME"]

        dataBase = mysql.connector.connect(
            host =db_name,
            user =db_user,
            passwd =db_pass
        )
        bucket_name = event['bucket']
        file_name = event['name']
        engine = create_engine(f'mysql://{db_user}:{db_pass}@{db_name}/PAYNEARBY') # enter your password and database names here

    except Exception as e:
        raise ValueError('Error while connecting to the Database : ' + str(e))

    try:
        df = pd.read_csv(f"gs://{bucket_name}/{file_name}",sep=",") # Replace Excel_file_name with your excel sheet name
        delete_file(bucket_name,file_name)
        df.rename(columns={'key': 'ID', 'place_name': 'PLACE_NAME', 'admin_name1':'ADMIN_NAME','latitude':'LATITUDE','longitude':'LONGITUDE','accuracy':'ACCURACY'}, inplace=True)
        df.to_sql('STG_PINCODE',con=engine,index=False,if_exists='replace') # Replace Table_name with your sql table name

    except Exception as e:
        raise ValueError('Error while processing the input file : ' + str(e))


    # preparing a cursor object
    cursorObject = dataBase.cursor()
    # using database
    cursorObject.execute("use PAYNEARBY")

    try:
        ETL(cursorObject)
    except Exception as e:
        raise ValueError(' Error while doing the ETL process '+ str(e))
    
    try:
        QA(cursorObject)
    except Exception as e:
        raise ValueError(' Error while doing the QA process '+ str(e))
    
    dataBase.commit()
    dataBase.close()