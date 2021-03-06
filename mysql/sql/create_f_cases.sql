create table f_cases(
        id integer  NOT NULL AUTO_INCREMENT, 
        cid varchar(20) not null ,
        priority_id integer not null, 
        createdDt_id integer not null, 
        createdDate datetime not null, 
        aid varchar(20) , 
        analyst_id integer , 
        pid varchar(20) , 
        product_id integer, 
        assignedDt_id integer,
        responseDt_id integer,
        resolveDt_id integer,
        assignedDate datetime, 
        responseDate datetime, 
        resolveDate datetime, 
        primary key(id),
        foreign key(priority_id) references d_priorities(id),
        foreign key(createdDt_id) references d_calendar(id),
        foreign key(analyst_id) references d_analysts(id),
        foreign key(product_id) references d_products(id),
        foreign key(assignedDt_id) references d_calendar(id),
        foreign key(responseDt_id) references d_calendar(id),
        foreign key(resolveDt_id) references d_calendar(id)
        );

