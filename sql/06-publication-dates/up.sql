alter table annotated_leads
    add column published_dt datetime;

create index annotated_leads_publication on annotated_leads(published_dt);

update annotated_leads join leads on leads.id = annotated_leads.lead_id
    set published_dt = discovered_dt
    where published_dt is null and is_published=1;