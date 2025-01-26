# What is Docker?

Is a set platform that delivers software as a service in packages
called containers. Containers are isolated from one another and bundled can
create their own software.

We have a data pipeline that will be run in a
container, isolated from others.

> CSV (Source) -> Data pipeline (python script) -> Table Postgres (destination)

We can couple several of these small pipelines into one big one each of them in an isolated container.

* CONTAINER:
  HOST COMPUTER (Windows)
  * Ubuntu 20.04
    * Data Pipeline
    * Python 3.9
    * Pandas
    * Postgres
  
* CONTAINER 2:
  * Postgres (DataBase)

* CONTAINER 3 (Optional):
  * pgAdmin -> For database manipulation.

**Docker benefits:** It will allow reproducibility since each image is a snapshot of the software. All the instructions to build an isolated part of software are set in this isolated environment. So tranfering the image to a different setting will allow to be run as in the setting it was created.

## What should we care about Docker

* Reproducibility
* Local Experiments
* Integration tests (CI/CD)
* Running pipelines on the cloud (AWS Batch, Kubernetes Jobs)
* Spark
* Serverless (AWS Lambda, Google Functions)

## Running Docker

The `Dockerfile` contains all the running steps to be run by Docker. 

To test docker in the terminal:
> docker run hello-world

This will pull the image from docker itself and works to test if works accordingly. Similarly, `docker run -it ubuntu bash` it will immediatly allow you to run interactively in the terminal we can modify things or delete folders but when running the command again, it will load the original version.

> docker run -it python:3.9

To build the image we created:
> docker build -t <name:tag> .<folder_dockerfile_is>
> docket build -t test:pandas .

To run the built image:
> docker run -it test:pandas

If changes are done to the Docker image then by keeping the same tag will overwrite the existing one. Thus reducing the latency time.

pipelines need to be self sufficient and perform tasks automatic, like loading data at a particular moment.

By adding arguments as entry points we can point Docker to start either from bash or python.

For example: ```docker run -it test:pandas <some_date>```

## Docker Compose

It is a way to run several Docker images.

## Connecting PostGres with docker

Using the docker image of postgres within docker helps to load the db with the data we want. To do so we need the following.

1. Docker initializer:

    ```bash
    docker run -it
    ```

2. Environmental variables: using the -e in the parameters. Will hold the User, password and name of the db.

    ```bash
    -e POSTGRES_USER=root \
    -e POSTGRES_PASSWORD=root \
    -e POSTGRES_DB=ny_taxi \
    ```

3. Volumes: it is a way to map a folder in our data system into the container. Since postgress is a db needs to hold locally a db and access the data, this also because when the image is closed, then it returns to the initial state.

    ```bash
    -v postgres-db-volume:var/lib/postgresql/data  \
    ```

4. Port: In order connect the host machine to the container, we need to specify a port that needs to be accessed.

    ```bash
    -p 5432:5432 \
    ```

5. Image name:

    ```bash
      postgres:13
    ```

Note: it is important to be aware of the path nature if windows or linux

```bash
docker run -it \
  -e POSTGRES_USER=root \
  -e POSTGRES_PASSWORD=root \
  -e POSTGRES_DB=ny_taxi \
  -v /home/cperez/local_projects/de_zoomcamp_25/module_01/2_docker_sql/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:13
```

## PGCLI

Python library to acces the database.

```bash
pgcli -h localhost -p 5433 -u root -d ny_taxi 
```

To evaluate what is in the DB -> ```\dt```

To get the DDL (Data Definition Language)

```bash
print(pd.io.sql.get_schema(df, name="yellow_taxi_data"))

CREATE TABLE "yellow_taxi_data" (
"VendorID" INTEGER,
  "tpep_pickup_datetime" TIMESTAMP,
  "tpep_dropoff_datetime" TIMESTAMP,
  "passenger_count" REAL,
  "trip_distance" REAL,
  "RatecodeID" REAL,
  "store_and_fwd_flag" TEXT,
  "PULocationID" INTEGER,
  "DOLocationID" INTEGER,
  "payment_type" INTEGER,
  "fare_amount" REAL,
  "extra" REAL,
  "mta_tax" REAL,
  "tip_amount" REAL,
  "tolls_amount" REAL,
  "improvement_surcharge" REAL,
  "total_amount" REAL,
  "congestion_surcharge" REAL,
  "airport_fee" REAL
)
```

The output of the cindicate the modus in which the data needs to be ingested in postgres. To do that is needed a platform to perform the connection and write data into the database.

One best practice is not to upload the entire dataset in one go but chnk it into pieces.