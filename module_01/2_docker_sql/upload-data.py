# %%
from time import time
import pandas as pd
import pyarrow.parquet as pq
# %%
pd.__version__
# %%
table = pq.read_table("yellow_tripdata_2021-01.parquet")
df = table.to_pandas()
df = df.head(100)
df

#%%
# content of this cell is how to create the engine for postgress
from sqlalchemy import create_engine

# %%
engine = create_engine('postgresql://root:root@localhost:5433/ny_taxi')

# %%
print(pd.io.sql.get_schema(df, name="yellow_taxi_data", con=engine))
# %%
table = pq.read_table("yellow_tripdata_2021-01.parquet")
df = table.to_pandas()
df = df.head(10000)
df.head()
# %%
df.to_sql(name='yellow_taxi_data', con=engine, if_exists='replace', index=False)
df.head(0)
# %%
# Open the Parquet file
# Define the SQL engine connection

# Open the Parquet file
file_path = "yellow_tripdata_2021-01.parquet"
table = pq.read_table(file_path)

# Define the chunk size
chunk_size = 100  # Adjust the chunk size as needed
total_rows = table.num_rows

# Start reading and processing chunks
for start in range(0, total_rows, chunk_size):
    t_start = time()

    # Slice the table to get the chunk (e.g., first 100 rows)
    end = min(start + chunk_size, total_rows)
    df_chunk = table.slice(start, end - start).to_pandas()

    # Insert the chunk into SQL
    df_chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append', index=False)

    t_end = time()
    print(f'Inserted chunk from {start} to {end}, took %.3f seconds' % (t_end - t_start))
    
# %%
