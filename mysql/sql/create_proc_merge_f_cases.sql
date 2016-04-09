create procedure merge_f_cases()
begin
# Create a staging table and populate it with rows from new or updated cases and logs 
create temporary table temp_new_f_cases as 
select
    cases.cid,
	cases.Priority,
	ifnull(DATE_FORMAT(cases.CreatedDate,'%Y%m%d'),-1)  CreatedDt_id,
	cases.CreatedDate,
	cases.aid,
	ifnull(analysts.id,-1) analyst_id,
	cases.pid,
	ifnull(p.id,-1) product_id,
	ifnull(DATE_FORMAT(dates.AssignedDt,'%Y%m%d'),-1) AssignedDt_id,
	ifnull(DATE_FORMAT(dates.ResponseDt,'%Y%m%d'),-1)  ResponseDt_id,
	ifnull(DATE_FORMAT(dates.ResolveDt,'%Y%m%d'),-1)  ResolveDt_id,
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
and ifnull(dates.AssignedDt,cases.CreatedDate) between analysts.StartDate and ifnull(analysts.EndDate,CURRENT_DATE)
order by analysts.id;

start transaction;
#update existing cases
update f_cases 
  inner join temp_new_f_cases
  on f_cases.cid=temp_new_f_cases.cid
set 
     f_cases.Priority_id=temp_new_f_cases.Priority
	,f_cases.aid = temp_new_f_cases.aid
	,f_cases.analyst_id=temp_new_f_cases.analyst_id
	,f_cases.pid=temp_new_f_cases.pid
	,f_cases.product_id=temp_new_f_cases.product_id
	,f_cases.AssignedDt_id=temp_new_f_cases.AssignedDt_id
	,f_cases.ResponseDt_id=temp_new_f_cases.ResponseDt_id
	,f_cases.ResolveDt_id=temp_new_f_cases.ResolveDt_id
	,f_cases.AssignedDate=temp_new_f_cases.AssignedDt
	,f_cases.ResponseDate=temp_new_f_cases.ResponseDt
	,f_cases.ResolveDate=temp_new_f_cases.ResolveDt;


#insert new cases
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
#End transaction and commit
commit;


#Drop the staging table
drop table temp_new_f_cases;
end;
 


