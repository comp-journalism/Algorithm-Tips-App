from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, MetaData,
                        SmallInteger, String, Table, UniqueConstraint)

meta = MetaData()

users = Table('users', meta,
              Column('id', Integer, primary_key=True),
              Column('external_id', String(64), nullable=False),
              Column('external_type', String(16), nullable=False),
              UniqueConstraint('external_id', 'external_type')
              )

leads = Table('leads', meta,
              Column('id', Integer, primary_key=True),
              Column('discovered_dt', DateTime),
              Column('query_term', String, nullable=False),
              Column('link', String, nullable=False),
              Column('domain', String, nullable=False),
              Column('jurisdiction', String, nullable=False),
              Column('source', String, nullable=False),
              Column('people', String, nullable=False),
              Column('organizations', String, nullable=False),
              Column('document_ext', String, nullable=False),
              Column('document_relevance', Float, nullable=False),
              )

annotated_leads = Table('annotated_leads', meta,
                        Column('id', Integer, primary_key=True),
                        Column('lead_id', None, ForeignKey('leads.id')),
                        Column('name', String, nullable=False),
                        Column('description', String, nullable=False),
                        Column('topic', String, nullable=False),
                        Column('is_published', SmallInteger, nullable=False),
                        Column('published_dt', DateTime),
                        )

flags = Table('flags', meta,
              Column('id', Integer, primary_key=True),
              Column('lead_id', None, ForeignKey('leads.id')),
              Column('user_id', None, ForeignKey('users.id')),
              UniqueConstraint('lead_id', 'user_id')
              )

alerts = Table('alerts', meta,
               Column('id', Integer, primary_key=True),
               Column('user_id', None, ForeignKey('users.id')),
               Column('federal_source', String),
               Column('regional_source', String),
               Column('local_source', String),
               Column('frequency', SmallInteger, nullable=False),
               Column('recipient', String, nullable=False),
               Column('filter', String, nullable=False),
               )

crowd_ratings = Table('crowd_ratings', meta,
                      Column('id', Integer, primary_key=True),
                      Column('lead_id', None, ForeignKey('leads.id')),
                      Column('controversy', Float),
                      Column('surprise', Float),
                      Column('magnitude', Float),
                      Column('societal_impact', Float),
                      Column('news_value', Float),
                      Column('controversy_explanation', String),
                      Column('surprise_explanation', String),
                      Column('magnitude_explanation', String),
                      Column('societal_impact_explanation')
                      )

confirmed_emails = Table('confirmed_emails', meta,
                         Column('id', Integer, primary_key=True),
                         Column('user_id', None, ForeignKey('users.id')),
                         Column('email', String, nullable=False),
                         )

pending_confirmations = Table('pending_confirmations', meta,
                              Column('id', Integer, primary_key=True),
                              Column('user_id', None, ForeignKey('users.id')),
                              Column('email', String, nullable=False),
                              Column('send_date', DateTime, nullable=False)
                              )

sent_alerts = Table('sent_alerts', meta,
                    Column('id', Integer, primary_key=True),
                    # this is not a true foreign key because we will keep dangling
                    # references around
                    Column('alert_id', Integer, nullable=False),
                    Column('send_date', DateTime, nullable=False),
                    Column('user_id', None, ForeignKey('users.id')),
                    Column('federal_source', String),
                    Column('regional_source', String),
                    Column('local_source', String),
                    Column('frequency', SmallInteger, nullable=False),
                    Column('recipient', String, nullable=False),
                    Column('db_link', String, nullable=False),
                    Column('filter', String, nullable=False),
                    )

sent_alert_contents = Table('sent_alert_contents', meta,
                            Column('id', Integer, primary_key=True),
                            Column('send_id', None, ForeignKey(
                                'sent_alerts.id')),
                            Column('lead_id', None, ForeignKey('leads.id')),
                            )
