# Module 02: Orchestration

For this module __KESTRA__  will be used as orchestrator.

__KESTRA__ is an open-source, event-driven orchestration platform that simplifies building both scheduled and event-driven workflows. By adopting Infrastructure as Code practices for data and process orchestration, Kestra enables you to build reliable workflows with just a few lines of YAML.

## Introduction to Orchestration

Orchestration as the name implies comes from musical orchestra. Where several instruments are needed but the timing when each of them is played varies, some of can be simultaneously or sequential.

All orchestas need a director to give orders about when which instrument needs to be played. Similar in code, having all those python scripts that do several things but running independently is just a small part of the overall job. Is about how we can run them together and from the user's perspective to understand what is going on and when the complexity can be dealt with. 

## KESTRA

Can be defined as All-in-one automation & orchestration platform. It will allows us to perform processes as:

* ETL
* API Orchestration
* Scheduled & Event-driven Workflows
* Batch data pipelines
* Interactive Conditional inputs

In addition ot the multi language support it allows to dashboard the pipeline and overall process.

## ETL introduction

A simple pipeline will be composed by:

1. Extract
2. Transform
3. Query

To achieve the connection between the modules the workflow will require an ID, unique for the workflow and the namespace which acts like a folder where the modules are stored. In more complex workflows the namespace can direct to the operation to be performed or the team.

__inputs__: Are values that can be passed at the start of the execution and define what is going to happen.

__Tasks:__ defines the steps to be executed in the workflow, they can be sequencial and the output will be the input of the next step.

### Starting with KESTRA

It does needs a docker image to download:

```docker
docker run --pull=always --rm -it \
    -p 8080:8080 \
    --user=root \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    kestra/kestra:latest-full server local
```

When the command is finished, localhost:8080 will have the landing page.

It is important to remember that:

* Workflows are simple flows
* YAML is the default language.
* Works with any language.

### Example

```YAML
id: getting_started
namespace: get_started
tasks:
    - id: hello_world
    type: io.kestra.core.tasks.log.Log
    message: Hello World!!
```

__outputs__: Are created for each tasks and can be used in the next or other tasks.

__triggers:__ It useful to execute tasks when is wanted or certains conditions are met.

### Docker compose

This alternative allows to have several instances connected and a permanent db. The normal Docker will delete all the instances when the ocntainer is shut down.

> https://github.com/kestra-io/kestra/blob/develop/docker-compose.yml

This part of the setup is defined in the environmental variable in the docker-compose.yml file.

```bash
datasources:
  postgres:
    url: jdbc:postgresql://postgres:5432/kestra
    driverClassName: org.postgresql.Driver
    username: kestra
    password: k3str4
kestra:
  server:
    basicAuth:
      enabled: false
      username: "admin@kestra.io" # it must be a valid email address
      password: kestra
  repository:
    type: postgres
  storage:
    type: local
    local:
      basePath: "/app/storage"
  queue:
    type: postgres
  tasks:
    tmpDir:
      path: "/tmp/kestra-wd/tmp"
  url: "http://localhost:8080/"
```

## 2.1 ETL pipelines with Postgres

The data comes split in several different parts by and corresponds to the taxi data from NYC from 2019 to 2021.

We can generate a workflow to extract the data and process the data in several tasks.

1. Retrieve the data from the repository: By using inputs we can specify the values of the kind of taxi, either yellow or green and defaults.

    Additionally, we can specify selectors by year and month(s).

    One way to ease the process of changing names of variables is to defining variables that will dynamically change the value as is needed.

```YAML
inputs:
  - id: taxi
    type: SELECT
    displayName: Select taxi type
    values: [yellow, green]
    defaults: yellow

variables:
  file: "{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv"
  staging_table: "public.{{inputs.taxi}}_tripdata_staging"
  table: "public.{{inputs.taxi}}_tripdata"
  data: "{{outputs.extract.outputFiles[inputs.taxi ~ '_tripdata_' ~ inputs.year ~ '-' ~ inputs.month ~ '.csv']}}"

tasks:
  - id: set_label
    type: io.kestra.plugin.core.execution.Labels
    labels:
      file: "{{render(vars.file)}}"
      taxi: "{{inputs.taxi}}"  
```

The variables task will generate the csv with the right structure based on the input data. That is followed by the task to asign the label to the file itself. the sintax ```{{inputs.}}``` is equivalent to f-strings in python.  

An additional task can be set ther SQL schema to map the data to the db in the correct format. We can split the table creation in 2 parts, the first mapping the data and the second to append extra data. IN case of new columns appear as well.

When all the changes and data cleaning are done in the staging table we can simply merge it to the main table which will receive the data as the months pass.

One last step (optional) is to remove the data since is already in the table and we dont need the original file anymore.

## 2.2 Managing schedules and Backfills

In __2.1__, we made a staging table that loads data from CSV files and after several transformations it merges into the main table where all the data is used. However, that works when the data ammount is low. 

What if data comes regularly?

We can use triggers connected to the variables to be used as scheduler.

```yaml
triggers:
  - id: green_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 1 * *"
    inputs:
      taxi: green

  - id: yellow_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 10 1 * *"
    inputs:
      taxi: yellow
```

We have 2 triggers using crontab being ```0 9 1 * *```  every month on the first day at 10 am. 

By having the triggers we can do backfills executions which are executions of the missing dates. For example fetch data from 2019 in 2025.

> It is important to set the concurrency level low to execute the triggers to avoid multiple flows overwtiting multiple months in that staging table. We want to avoid not truncating the table while other table is being written r creating new ids, it will make a mess in PostgreSQL.

## 2.3 Orchestrate dbt models with PostgreSQL and Kestra

DBT can help to automate the ETL pipeline, the main difference to the steps before is that with DBT we can extract the data directly from Github, load straight into a table and then perform the needed transformations.

The DBT cli will be used to connect to PostgreSQL so the raw data is processed and transformed, this can be done in parallel. One of the benefits is that DBT can create different table visualizations that can be connected to each other.

## 2.4 ^ 2.5 ^ 2.6 Google Cloud Platform and ETL pipelines

It is important to have the pipeline set already to work with BigQuery so set GCP is the only thing needed. The main difference is instead of using PostgreSQL to upload the data we will upload it directly into a datalake.

Afterwards, BigQuery will take the CSV file to create a DB, the cloud will use the staging and final data merged.

What will we need:

* GCP Service account
* GCP region ID
* Project ID
* Bucket ID

We can use key-value pairs in Kestra to give access to the GCP service account.

```yaml

tasks:
  - id: gcp_project_id
    type: io.kestra.plugin.core.kv.Set
    key: GCP_PROJECT_ID
    kvType: STRING
    value: kestra-sandbox # TODO replace with your project id

  - id: gcp_location
    type: io.kestra.plugin.core.kv.Set
    key: GCP_LOCATION
    kvType: STRING
    value: europe-west2

  - id: gcp_bucket_name
    type: io.kestra.plugin.core.kv.Set
    key: GCP_BUCKET_NAME
    kvType: STRING
    value: your-name-kestra # TODO make sure it's globally unique!

  - id: gcp_dataset
    type: io.kestra.plugin.core.kv.Set
    key: GCP_DATASET
    kvType: STRING
    value: zoomcamp
```

Steps:

1. Create a new project on GCP
2. Create a new servide account, with a role of storage adming and bigQuery.
3. Go to service account to create a new key in JSON and download. Then paste it in the Kestre key-value store.
4. Then update the values like bucket and unique values.
5. After executing all the values will be updated in the workspace created.
6. The setup task will take the following YAML

    ```yaml
    id: 05_gcp_setup
    namespace: zoomcamp

    tasks:
    - id: create_gcs_bucket
        type: io.kestra.plugin.gcp.gcs.CreateBucket
        ifExists: SKIP
        storageClass: REGIONAL
        name: "{{kv('GCP_BUCKET_NAME')}}" # make sure it's globally unique!

    - id: create_bq_dataset
        type: io.kestra.plugin.gcp.bigquery.CreateDataset
        name: "{{kv('GCP_DATASET')}}"
        ifExists: SKIP

    pluginDefaults:
    - type: io.kestra.plugin.gcp
        values:
        serviceAccount: "{{kv('GCP_CREDS')}}"
        projectId: "{{kv('GCP_PROJECT_ID')}}"
        location: "{{kv('GCP_LOCATION')}}"
        bucket: "{{kv('GCP_BUCKET_NAME')}}"
    ```

    And will set the values created in the previous step to add the information.

7. After creating and setting up GCP, the questions is what is the storage used for? Tecnically is to store unstructured data as an object. But also has the option to be used as data warehouse for structured data meaining columns and rows. So similaro to 2.2. We need to structure the inputs (year, month, taxi type, etc), followed by the labels and followinth of the extractions.

8. The tasks will be upload the data to GCS as a raw CSV file.

9. Upload to bigQuery, similat to PostgreSQL we need to create an schema to map the CSV file into the corresponding BigQuery db, this is done as a task.
10. After the data transformation is done we can purge the original data to save storage since everything is saved in the database.

## 2.7 Manage Schedules and backfils with GCP

It is a way to optimize to include triggers that will schedule the pipeline to run at different times automatically. The topology then will not change much with exception of the variables where instead of using inputs we use the trigger to collect the data:

```yaml

variables:
  file: "{{inputs.taxi}}_tripdata_{{trigger.date | date('yyyy-MM')}}.csv"
  gcs_file: "gs://{{kv('GCP_BUCKET_NAME')}}/{{vars.file}}"
  table: "{{kv('GCP_DATASET')}}.{{inputs.taxi}}_tripdata_{{trigger.date | date('yyyy_MM')}}"
  data: "{{outputs.extract.outputFiles[inputs.taxi ~ '_tripdata_' ~ (trigger.date | date('yyyy-MM')) ~ '.csv']}}"
```

The addition of ```{{trigger.date | date('yyyy-MM' )}}``` will not work if we run the pipeline manually since is the information comes with the trigger.

## 2.8 Orchestrate DBT models with BigQuery

We can use DBT to transform thedata previously unuseful into something that is structured and easy to manipulate. The data:

```yaml
id: 07_gcp_dbt
namespace: zoomcamp
inputs:
  - id: dbt_command
    type: SELECT
    allowCustomValue: true
    defaults: dbt build
    values:
      - dbt build
      - dbt debug # use when running the first time to validate DB connection

tasks:
  - id: sync
    type: io.kestra.plugin.git.SyncNamespaceFiles
    url: https://github.com/DataTalksClub/data-engineering-zoomcamp
    branch: main
    namespace: "{{flow.namespace}}"
    gitDirectory: 04-analytics-engineering/taxi_rides_ny
    dryRun: false
    # disabled: true # this Git Sync is needed only when running it the first time, afterwards the task can be disabled

  - id: dbt-build
    type: io.kestra.plugin.dbt.cli.DbtCLI
    env:
      DBT_DATABASE: "{{kv('GCP_PROJECT_ID')}}"
      DBT_SCHEMA: "{{kv('GCP_DATASET')}}"
    namespaceFiles:
      enabled: true
    containerImage: ghcr.io/kestra-io/dbt-bigquery:latest
    taskRunner:
      type: io.kestra.plugin.scripts.runner.docker.Docker
    inputFiles:
      sa.json: "{{kv('GCP_CREDS')}}"
    commands:
      - dbt deps
      - "{{ inputs.dbt_command }}"
    storeManifest:
      key: manifest.json
      namespace: "{{ flow.namespace }}"
    profiles: |
      default:
        outputs:
          dev:
            type: bigquery
            dataset: "{{kv('GCP_DATASET')}}"
            project: "{{kv('GCP_PROJECT_ID')}}"
            location: "{{kv('GCP_LOCATION')}}"
            keyfile: sa.json
            method: service-account
            priority: interactive
            threads: 16
            timeout_seconds: 300
            fixed_retries: 1
        target: dev
description: |
  Note that you need to adjust the models/staging/schema.yml file to match your database and schema. Select and edit that Namespace File from the UI. Save and run this flow. Once https://github.com/DataTalksClub/data-engineering-zoomcamp/pull/565/files is merged, you can ignore this note as it will be dynamically adjusted based on env variables.
  ```yaml
  sources:
    - name: staging
      database: kestra-sandbox 
      schema: zoomcamp
    ```
```
