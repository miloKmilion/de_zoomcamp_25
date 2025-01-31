# This will pull the raw image of python 3.9 from Docker.
FROM python:3.9

# Initial command with installables.
RUN apt-get install wget
RUN pip install pandas sqlalchemy pyarrow psycopg2 requests

WORKDIR /app
# Copy will add the file in the host machine to the destination.
COPY ingest_data.py ingest_data.py 

# To override and use bash as typing, and not python. 
ENTRYPOINT [ "python", "ingest_data.py" ]