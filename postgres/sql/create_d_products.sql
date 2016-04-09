create table d_products(
	id SERIAL,
	pid varchar(20) not null,
	ProductLine varchar(100) not null,
	ProductGroup varchar(100) not null,
	Product varchar(100) not null,
	primary key(id));

