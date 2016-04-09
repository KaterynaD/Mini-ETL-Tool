create procedure merge_scdt2_d_analysts()
begin
#if there is a change in historical fields, close the current active record and create a new one using insert statement later
update d_analysts a1
 set isactive=False
    ,enddate=(select date_add(an.updateddate, interval -1 second) from analysts an where an.aid=a1.aid)
 where a1.id  in (select a1.id from analysts an where a1.isactive=True and an.aid=a1.aid and (a1.team<>an.team or a1.skills<>an.skills));

 #update data in NON historical fields
update d_analysts
	inner join analysts
	on analysts.aid=d_analysts.aid
 set d_analysts.name=analysts.name; 
 
#insert new records
insert into d_analysts (aid, name, team, skills, StartDate)
select aid, name, team, skills, updateddate from analysts
where aid not in (select aid from d_analysts where isactive=True);

commit;
end;


