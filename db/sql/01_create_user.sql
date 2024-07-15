connect system/consult7@ORCLPDB1

create user API
/

grant
    create session,
    create table,
    create procedure,
    create type,
    create sequence,
    select any dictionary,
    unlimited tablespace
to API
/

begin

    for r in
            ( select role
              from dba_roles
              where role in ('SODA_APP', 'AQ_ADMINISTRATOR_ROLE')
            ) loop
        execute immediate 'grant ' || r.role || ' to API';
    end loop;

end;
/

alter user API identified by "API123"
/

exit;
