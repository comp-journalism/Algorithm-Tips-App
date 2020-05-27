create table pending_confirmations (
    id integer not null primary key auto_increment,
    user_id integer not null,
    email text not null,
    send_date datetime not null default now(),
    foreign key (user_id) references users(id)
);

create table confirmed_emails (
    id integer not null primary key auto_increment,
    user_id integer not null,
    email text not null,
    foreign key (user_id) references users(id)
);