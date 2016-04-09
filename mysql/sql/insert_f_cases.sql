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
    cases.cid,
	cases.Priority,
	ifnull(DATE_FORMAT(cases.CreatedDate,'%Y%m%d'),-1 ) CreatedDt_id,
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
order by analysts.id
);

