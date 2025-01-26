# This will pull the raw image of python 3.9 from Docker.
FROM python:3.9

# Initial command with installables.
RUN pip install pandas

WORKDIR /app
# Copy will add the file in the host machine to the destination.
COPY pipeline.py pipeline.py

# To override and use bash as typing, and not python. 
ENTRYPOINT [ "python", "pipeline.py" ]