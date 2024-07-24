create user &user
/

grant
    create session,
    create table,
    create procedure,
    create type,
    create sequence,
    select any dictionary,
    unlimited tablespace
to &user
/

begin

    for r in
            ( select role
              from dba_roles
              where role in ('SODA_APP', 'AQ_ADMINISTRATOR_ROLE')
            ) loop
        execute immediate 'grant ' || r.role || ' to &user';
    end loop;

end;
/

alter user &user identified by "&pw"
/
