import requests
import pandas as pd
import pyarrow.parquet as pq
from time import time
from sqlalchemy import create_engine

def process_data(url, user, password, host, port, db, table_name, chunk_size=100000):
    """Downloads data from a given URL, determines its format, and ingests it into PostgreSQL."""
    # Determine the correct file format
    if url.endswith('.parquet'):
        file_name = 'output.parquet'
    elif url.endswith('.csv.gz'):
        file_name = 'output.csv.gz'
    else:
        raise ValueError("Unsupported file format. Only '.parquet' and '.csv.gz' are supported.")
    
    # Download the file securely
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File downloaded successfully: {file_name}")
    else:
        raise Exception(f"Failed to download file: HTTP {response.status_code}")
    
    # Create the database engine
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # Process the file based on its format
    if file_name.endswith('.parquet'):
        ingest_parquet_to_postgresql(file_name, table_name, engine, chunk_size)
    elif file_name.endswith('.csv.gz'):
        ingest_csv_to_postgres(file_name, table_name, engine, chunk_size)


def ingest_parquet_to_postgresql(parquet_file, table_name, engine, chunk_size=100000):
    """Ingests data from a Parquet file into PostgreSQL in chunks."""
    table = pq.read_table(parquet_file)
    total_rows = table.num_rows
    
    print(f"Starting ingestion of {total_rows} rows from '{parquet_file}' into table '{table_name}'.")

    # Process the data in chunks
    for start in range(0, total_rows, chunk_size):
        t_start = time()
        
        # Slice the table to get the current chunk
        end = min(start + chunk_size, total_rows)
        df_chunk = table.slice(start, end - start).to_pandas()
        
        # Insert into PostgreSQL
        df_chunk.to_sql(table_name, engine, if_exists='append', index=False)
        
        t_end = time()
        print(f"Inserted rows {start} to {end}, took {t_end - t_start:.3f} seconds.")
    
    print(f"Finished ingesting data into table '{table_name}'.")


def ingest_csv_to_postgres(csv_file, table_name, engine, chunksize=100000):
    """Ingests data from a CSV file into PostgreSQL in chunks."""
    # Initialize CSV iterator
    df_iter = pd.read_csv(csv_file, iterator=True, chunksize=chunksize)

    # Get the first chunk and initialize the table schema
    df = next(df_iter)
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

    # Create the table schema using the first chunk
    df.head(0).to_sql(name=table_name, con=engine, if_exists='replace')
    df.to_sql(name=table_name, con=engine, if_exists='append')
    print(f"Schema created and first chunk inserted into table '{table_name}'.")

    # Process the remaining chunks
    while True:
        try:
            t_start = time()

            # Get the next chunk
            df = next(df_iter)

            # Convert datetime columns
            df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
            df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

            # Insert the chunk into the database
            df.to_sql(name=table_name, con=engine, if_exists='append', index=False)

            t_end = time()
            print(f"Inserted another chunk into '{table_name}', took {t_end - t_start:.3f} seconds.")

        except StopIteration:
            print(f"Finished ingesting data into the PostgreSQL database for table '{table_name}'.")
            break


process_data(
    url='https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet',
    user='root',
    password='root',
    host='pg-database',
    port='5432',
    db='ny_taxi',
    table_name='yellow_taxi_data',
    chunk_size=100000
)
