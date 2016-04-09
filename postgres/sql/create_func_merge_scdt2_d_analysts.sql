create or replace function merge_scdt2_d_analysts()
returns void as $$
begin
--if there is a change in historical fields, close the current active record and create a new one using insert statement later
update d_analysts a1
 set isactive=False
    ,enddate=(select an.updateddate - interval '1 second' from analysts an where an.aid=a1.aid)
 where a1.id  in (select a1.id from analysts an where a1.isactive=True and an.aid=a1.aid and (a1.team<>an.team or a1.skills<>an.skills));

 --update data in NON historical fields
update d_analysts
set name=analysts.name
from analysts
 where analysts.aid=d_analysts.aid;

--insert new records
insert into d_analysts (aid, name, team, skills, StartDate)
select aid, name, team, skills, updateddate from analysts
where aid not in (select aid from d_analysts where isactive=True);

end;
$$ LANGUAGE plpgsql
