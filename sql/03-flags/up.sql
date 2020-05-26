create table flags (
    id integer not null primary key auto_increment,
    lead_id integer not null,
    user_id integer not null,
    unique key (lead_id, user_id),
    foreign key (lead_id) references leads(id),
    foreign key (user_id) references users(id)
);