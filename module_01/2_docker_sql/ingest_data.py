import os
import argparse
import requests


from time import time

import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import create_engine


def process_data(url, user, password, host, port, db):
    # Determine the correct file format
    if url.endswith('.parquet'):
        file_name = 'output.parquet'
    elif url.endswith('.csv.gz'):
        file_name = 'output.csv.gz'
    else:
        raise FileNotFoundError("Unsupported file format or URL.")
    
    # Download the file securely
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        raise Exception(f"Failed to download file: {response.status_code}")
    
    # Create the database engine
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    
    # Read the downloaded file and return the DataFrame
    if file_name.endswith('.parquet'):
        df = pq.read_table(file_name).to_pandas()
        return df
    elif file_name.endswith('.csv.gz'):
        df_iter = pd.read_csv(file_name, iterator=True, chunksize=100000)
        
        # Example: process the first chunk (or process all iteratively if needed)
        df = next(df_iter)
        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
        df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
        
        # Example: Save to database
        df.to_sql('ny_taxi_data', engine, if_exists='replace', index=False)
        
        return df



def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    
    
    # Finding the correct data format
    if url.endswith('.parquet'):
        file_name =  'output.parquet'
    elif url.endswith('.csv.gz'):
        file_name = 'output.csv.gz'
    else:
        FileNotFoundError
        
    os.system(f'wget {url} -O {file_name}')

    # Creating the engine:
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
  
    if file_name.endswith('.parquet'):
        df = pq.read_table(file_name)
        return df
    elif file_name.endswith('.csv') or file_name.endswith('.csv.gz'):
        df_iter = pd.read_csv(file_name, iterator=True, chunksize=100000)

        df = next(df_iter)

        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        return df
    
    


    
# https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet
    
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    parser.add_argument('--table_name', required=True, help='name of the table where we will write the results to')
    parser.add_argument('--url', required=True, help='url of the csv file')

    args = parser.parse_args()

    main(args)