create table users (
    id integer not null primary key auto_increment,
    external_id varchar(64) not null,
    external_type varchar(16) not null,
    email text,
    unique key(external_id, external_type)
);