create table fg1n_twincore_user
        (ID nvarchar2(100) not null,
         USERNAME nvarchar2(100) not null,
         HASHED_PASSWORD nvarchar2(300) not null,
         EMAIL nvarchar2(100),
         FULL_NAME nvarchar2(100))
/