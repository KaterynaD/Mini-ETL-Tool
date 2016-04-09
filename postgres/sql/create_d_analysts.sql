create table d_analysts(
    id  SERIAL,
	aid varchar(20) not null,
	name varchar(50) not null,
	team varchar(30) not null,
	skills varchar(50),
	StartDate  timestamp not null,
	EndDate  timestamp,
	isActive boolean not null default True,
	primary key(id)
	);
