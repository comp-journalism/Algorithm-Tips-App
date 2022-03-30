from sqlalchemy import Table, MetaData, text, Text, Column, ForeignKey, Float, MetaData, orm
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement
from sqlalchemy.sql.ddl import DropTable
from api.models import leads
import sqlalchemy_views


class View(Table):
    is_view = True


class CreateView(sqlalchemy_views.CreateView):
    def __init__(self, view):
        super().__init__(view.__view__, view.__definition__)


@compiles(DropTable)
def _compile_drop_table(element, compiler, **kwargs):
    if hasattr(element.element, 'is_view') and element.element.is_view:
        return compiler.visit_drop_view(element)

    # cascade seems necessary in case SQLA tries to drop 
    # the table a view depends on, before dropping the view
    return compiler.visit_drop_table(element) + ' CASCADE'

class average_leads:
    __view__ = View(
        'average_leads', MetaData(),
         Column('lead_id', None, ForeignKey(leads.c.id), primary_key=True),
         Column('average_news_value', Float)
    )

    __definition__ = text('SELECT lead_id, AVG(news_value) as average_news_value  FROM algorithm_tips_app.crowd_ratings GROUP BY lead_id')