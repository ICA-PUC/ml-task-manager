connect API/API123@ORCLPDB1

create table TASK
        (ID nvarchar2 not null,
         INSTANCE_TYPE nvarchar2 not null,
         ACCOUNT nvarchar2 not null,
         RUNNER_LOCATION nvarchar2 not null,
         SCRIPT_PATH nvarchar2 not null,
         DATASET_NAME nvarchar2 not null,
         EXPERIMENT_NAME nvarchar2 not null,
         JOB_ID number not null
        )
/

exit;
