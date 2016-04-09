create table d_analysts(
    id  integer NOT NULL AUTO_INCREMENT,
	aid varchar(20) not null,
	name varchar(50) not null,
	team varchar(30) not null,
	skills varchar(50),
	StartDate datetime not null,
	EndDate datetime,
	isActive boolean not null default True,
	primary key(id)
	);
