from sqlalchemy import Table, String, Integer, Column, MetaData, DateTime, Float, ForeignKey, SmallInteger, UniqueConstraint

meta = MetaData()

users = Table('users', meta,
              Column('id', Integer, primary_key=True),
              Column('external_id', String(64), nullable=False),
              Column('external_type', String(16), nullable=False),
              Column('email', String),
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
                        Column('publication_date', DateTime),
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
