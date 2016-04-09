start transaction;

#insert new records

insert into d_analysts (aid, name, team, skills, StartDate)
select aid, name, team, skills,'2010-01-01 00:00:00' from analysts_2010
where aid not in (select aid from d_analysts where isactive=True);

#next year data source
#if there is a change in historical fields, close the current active record and create a new one using insert statement later
update d_analysts a1
 set isactive=False
    ,enddate='2010-12-31 23:59:59'
 where id  in (select a1.id from analysts_2011 an where a1.isactive=True and an.aid=a1.aid and (a1.team<>an.team or a1.skills<>an.skills));

#update data in NON historical fields
update d_analysts
    inner join analysts_2011
    on d_analysts.aid=analysts_2011.aid
 set d_analysts.name=analysts_2011.name;

#insert new records
insert into d_analysts (aid, name, team, skills, StartDate)
select aid, name, team, skills, '2011-01-01 00:00:00' from analysts_2011
where aid not in (select aid from d_analysts where isactive=True);

#next year data source
#if there is a change in historical fields, close the current active record and create a new one using insert statement later
update d_analysts a1
 set isactive=False
    ,enddate='2011-12-31 23:59:59'
 where id  in (select a1.id from analysts_2012 an where a1.isactive=True and an.aid=a1.aid and (a1.team<>an.team or a1.skills<>an.skills));

#update data in NON historical fields
update d_analysts
    inner join analysts_2012
    on d_analysts.aid=analysts_2012.aid
 set d_analysts.name=analysts_2012.name;

#insert new records
insert into d_analysts (aid, name, team, skills, StartDate)
select aid, name, team, skills, '2012-01-01 00:00:00' from analysts_2012
where aid not in (select aid from d_analysts where isactive=True);

#next year data source
#if there is a change in historical fields, close the current active record and create a new one using insert statement later
update d_analysts a1
 set isactive=False
    ,enddate='2012-12-31 23:59:59'
 where id  in (select a1.id from analysts_2013 an where a1.isactive=True and an.aid=a1.aid and (a1.team<>an.team or a1.skills<>an.skills));

#update data in NON historical fields
update d_analysts
    inner join analysts_2013
    on d_analysts.aid=analysts_2013.aid
 set  d_analysts.name=analysts_2013.name;

#insert new records
insert into d_analysts (aid, name, team,skills, StartDate)
select aid, name, team, skills, '2013-01-01 00:00:00' from analysts_2013
where aid not in (select aid from d_analysts where isactive=True);

#next year data source
#if there is a change in historical fields, close the current active record and create a new one using insert statement later
update d_analysts a1
 set isactive=False
    ,enddate='2013-12-31 23:59:59'
 where id  in (select a1.id from analysts_2014 an where a1.isactive=True and an.aid=a1.aid and (a1.team<>an.team or a1.skills<>an.skills));

#update data in NON historical fields
update d_analysts
    inner join analysts_2014
    on d_analysts.aid=analysts_2014.aid
 set d_analysts.name=analysts_2014.name;

#insert new records
insert into d_analysts (aid, name, team, skills, StartDate)
select aid, name, team, skills, '2014-01-01 00:00:00' from analysts_2014
where aid not in (select aid from d_analysts where isactive=True);

commit;


