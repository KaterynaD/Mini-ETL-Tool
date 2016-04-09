create or replace function merge_f_cases()
returns void as $$
begin
-- Create a staging table and populate it with rows from new or updated cases and logs
create temporary table temp_new_f_cases as
select
    cases.cid,
        cases.Priority,
        nullif(cast(to_char(cases.CreatedDate,'yyyymmdd') as integer),-1)  CreatedDt_id,
        cases.CreatedDate,
        cases.aid,
        nullif(analysts.id,-1) analyst_id,
        cases.pid,
        nullif(p.id,-1) product_id,
        nullif(cast(to_char(dates.AssignedDt,'yyyymmdd') as integer),-1) AssignedDt_id,
        nullif(cast(to_char(dates.ResponseDt,'yyyymmdd') as integer),-1)  ResponseDt_id,
        nullif(cast(to_char(dates.ResolveDt,'yyyymmdd') as integer),-1)  ResolveDt_id,
        dates.AssignedDt,
        dates.ResponseDt,
        dates.ResolveDt
from
cases
left outer join
(select
  cid
 ,min(AssignedDt) AssignedDt
 ,min(ResponseDt) ResponseDt
 ,max(ResolveDt) ResolveDt
 from
(select
             cid
                ,case
     when event='Assigned to analyst' then
            min(dt)
     end AssignedDt
                ,case
     when event='Response' then
            min(dt)
     end ResponseDt
    ,case
      when event='Close' then
              max(dt)
      end ResolveDt
from logs
group by  cid
                 ,event
                 ) data
group by cid
) dates
on cases.cid=dates.cid
left outer join
d_products p on cases.pid=p.pid
left outer join
d_analysts analysts
on cases.aid=analysts.aid
and nullif(dates.AssignedDt,cases.CreatedDate) between analysts.StartDate and nullif(analysts.EndDate,CURRENT_DATE)
order by analysts.id;


--update existing cases
update f_cases
set
         Priority_id=temp_new_f_cases.Priority
        ,aid = temp_new_f_cases.aid
        ,analyst_id=temp_new_f_cases.analyst_id
        ,pid=temp_new_f_cases.pid
        ,product_id=temp_new_f_cases.product_id
        ,AssignedDt_id=temp_new_f_cases.AssignedDt_id
        ,ResponseDt_id=temp_new_f_cases.ResponseDt_id
        ,ResolveDt_id=temp_new_f_cases.ResolveDt_id
        ,AssignedDate=temp_new_f_cases.AssignedDt
        ,ResponseDate=temp_new_f_cases.ResponseDt
        ,ResolveDate=temp_new_f_cases.ResolveDt
from temp_new_f_cases
where f_cases.cid=temp_new_f_cases.cid;

--insert new cases
insert into f_cases
(   cid,
        Priority_id,
        CreatedDt_id,
        CreatedDate,
        aid,
        analyst_id,
        pid,
        product_id,
        AssignedDt_id,
        ResponseDt_id,
        ResolveDt_id,
        AssignedDate,
        ResponseDate,
        ResolveDate
)
(
select
    temp_new_f_cases.cid,
        temp_new_f_cases.Priority,
        temp_new_f_cases.CreatedDt_id,
        temp_new_f_cases.CreatedDate,
        temp_new_f_cases.aid,
        temp_new_f_cases.analyst_id,
        temp_new_f_cases.pid,
        temp_new_f_cases.product_id,
        temp_new_f_cases.AssignedDt_id,
        temp_new_f_cases.ResponseDt_id,
        temp_new_f_cases.ResolveDt_id,
        temp_new_f_cases.AssignedDt,
        temp_new_f_cases.ResponseDt,
        temp_new_f_cases.ResolveDt
from temp_new_f_cases
where temp_new_f_cases.cid not in (select f_cases.cid from f_cases)
);


--Drop the staging table
drop table temp_new_f_cases;

end;
$$ LANGUAGE plpgsql

