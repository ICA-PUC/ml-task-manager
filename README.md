# Machine Learning Task Manager API

The goal of the project is to build a dockerized service that will accept HTTPS requests with a multipart payload containing configuration and entrypoint files with the proper information about a new ML task that must be sent to the target cluster. The API server will be a FastAPI python server, connected to a PostgreSQL or SQLITE database.

## Installation instructions

Here we will provide installation instructions for a local cluster development environment using docker-compose and an *almost* "production ready" version for the Atena02 environment.

### Atena 02 Cluster

Here we will list the steps requried to install and run inside Atena 02 cluster.

1. Connect to Atena 02 running `ssh your_key@atn1mg4`
2. Go to destination folder (e.g `cd /nethome/projetos30/arcabouco_ml`)
3. Generate API's singularity image - `singularity build api.sif docker://humblebeaver/ml-task-manager`. Expect an output similar to:

```bash
INFO:    Creating SIF file...
INFO:    Build complete: api.sif
```

4. Clone this repo - `git clone https://github.com/ICA-PUC/ml-task-manager.git`
5. Copy the initialization script `run_api.srm` to destination folder - `cp ml-task-manager/run_api.srm ./`
6. Open the initialization script with your desired text editor and adjust as follows:
   1. **Line 17**: `export ROOT_API="..."` - Must reflect the API's absolute path, e.g:
  `export ROOT_API="/nethome/projetos30/arcabouco_ml/ml-task-manager"`.
   2. **Line 18**: `export SIF_PATH="..."` - Must reflect API's `.sif` absolute_path.
1. Open `template.env` and add your atena02 user and password.
2. Run the API using `sbatch run_api.srm`
3. Check provided node name using `squeue --me` and take note of the node name (e.g `atn1b05n14`)
4. Open a browser from within Petrobras Workspace and access `<node_name>:<port>/docs` (e.g `atn1b05n14:8008/docs`), you should see FastAPI's documentation page.

**NOTE**: If something doesn't work, you can check API logs using `cat log_api.txt`.

### Local Dev Cluster

We can build and run the developing system by calling the following single command:

```bash
docker-compose up -d --build
```

For the production environment, we can run

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

By doing so, docker will build the image and spin up the two containers in dettached mode, i.e. silently in the background. We can then go to localhost:8008/docs (for the dev container) and localhost:8009/docs for the prod container, in order to access the builtin API documentaion.

For monitoring and checking for errors, you can acompany the logs by issuing `docker-compose logs -f`.

If you must rebuild or restart the hole process, you can bring down the containers and the associated volumes with:

```bash
docker-compose down -v  # dev
docker-compose -f docker-compose.prod.yml down -v  # prod
```

### Sanity checks

To assure if it is all running correctly, we can connect to the database command prompt and list databases and relations

```bash
$ docker-compose exec db psql --username=ml-task-manager --dbname=ml-task-manager

psql (15.1)
Type "help" for help.

ml-task-manager=# \l

Name       |      Owner      | Encoding |  Collate   |   Ctype    | ICU Locale | Locale Provider |            Access privileges            
-----------------+-----------------+----------+------------+------------+------------+-----------------+-----------------------------------------
 ml-task-manager | ml-task-manager | UTF8     | en_US.utf8 | en_US.utf8 |            | libc            | 
 postgres        | ml-task-manager | UTF8     | en_US.utf8 | en_US.utf8 |            | libc            | 
 template0       | ml-task-manager | UTF8     | en_US.utf8 | en_US.utf8 |            | libc            | =c/"ml-task-manager"                   +
                 |                 |          |            |            |            |                 | "ml-task-manager"=CTc/"ml-task-manager"
 template1       | ml-task-manager | UTF8     | en_US.utf8 | en_US.utf8 |            | libc            | =c/"ml-task-manager"                   +
                 |                 |          |            |            |            |                 | "ml-task-manager"=CTc/"ml-task-manager"
(4 rows)

ml-task-manager=# \c ml-task-manager

You are now connected to database "ml-task-manager" as user "ml-task-manager".

ml-task-manager=# \dt

# May be different initially, if you don't have any task created
            List of relations
 Schema | Name | Type  |      Owner      
--------+------+-------+-----------------
 public | task | table | ml-task-manager
(1 row)

ml-task-manager=# \q
```

We can also check that the volume was created as well by running:

```bash
docker volume inspect ml-task-manager_postgres_data
```

You will get something like this:

```bash
[
    {
        "CreatedAt": "2024-04-01T09:54:45-03:00",
        "Driver": "local",
        "Labels": {
            "com.docker.compose.project": "ml-task-manager",
            "com.docker.compose.version": "2.24.7",
            "com.docker.compose.volume": "postgres_data"
        },
        "Mountpoint": "/var/lib/docker/volumes/ml-task-manager_postgres_data/_data",
        "Name": "ml-task-manager_postgres_data",
        "Options": null,
        "Scope": "local"
    }
]
```

## Usage instructions

Here we will describe how to properly consume the API's routes.

### `POST /new_task`

In order for the API to create and submit a new task, the user must provide two files within the `multipart` HTTP request: The JSON configuration file and the zipped folder with the required files to run its job.

Here is a sample of the config JSON file and a brief description of the required fields.

```JSON
{
  "dataset_name": "wine_classification",
  "model_params": {
    "n_estimators": 2,
    "random_state": 42
  },
  "runner_location": "atena02",
  "model_tracking": true,
  "tracking_uri": "experiments",
  "experiment_name": "atena_test",
  "command": "python3 script.py"
  "clusters": {
    "atena02": {
      "infra_config": {
        "instance_type": "cpu",
        "image_name": "sklearn_sample_latest",
        "account": "twinscie"
      }
    }
  }
}
```

- **dataset_name**: The name of the dataset `.csv` file.
- **runner_location**: Name of the target cluster (e.g `atena02`, `aws`, `azure`, etc.)
- **experiment_name**: Name of the experiment.
- **command**: The bash command to run from job node, e.g, `python3 some_script.py` or `mlflow run ...`.
- **instance_type**: The kind of slurm instance to host the job.
- **image_name**: The name of the `.sif` image to run the experiment.
- **account**: Slurm user and job owner's account name.
