create table alerts (
    id integer not null primary key auto_increment,
    user_id integer not null,
    federal_source text,
    regional_source text,
    local_source text,
    frequency smallint not null,
    recipient text not null,
    filter text not null,
    foreign key (user_id) references users(id)
);