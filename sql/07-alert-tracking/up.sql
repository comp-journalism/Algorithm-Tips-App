create table sent_alerts (
    id integer not null primary key auto_increment,
    alert_id integer not null, -- not setting FK so that we keep sent_alerts around and can track how many emails were sent for each alert
    send_date datetime not null,
    db_link text not null,
    -- alert fields
    user_id integer not null,
    federal_source text,
    regional_source text,
    local_source text,
    frequency smallint not null,
    recipient text not null,
    filter text not null,
    foreign key (user_id) references users(id)
);

create table sent_alert_contents (
    id integer not null primary key auto_increment,
    send_id integer not null,
    lead_id integer not null,
    foreign key (send_id) references sent_alerts(id),
    foreign key (lead_id) references leads(id),
    unique key (send_id, lead_id)
);