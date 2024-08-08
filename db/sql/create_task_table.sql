create table ffir_twincore_task
        (ID nvarchar2(100) not null,
         INSTANCE_TYPE nvarchar2(100) not null,
         IMAGE_NAME nvarchar2(100) not null,
         ACCOUNT nvarchar2(100) not null,
         RUNNER_LOCATION nvarchar2(100) not null,
         SCRIPT_PATH nvarchar2(200) not null,
         DATASET_NAME nvarchar2(100) not null,
         EXPERIMENT_NAME nvarchar2(100) not null,
         JOB_ID number(10) not null,
         PROJECT_PATH nvarchar2(200) not null)
/
