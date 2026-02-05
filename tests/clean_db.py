from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from school_manager.db import db
import school_manager.models

# # Create DB session
# # Initialize the db inside core, so it will contain the db session of Graphene.
# DATABASE_URL = 'mysql://graphene:graphene@localhost/graphene?charset=utf8'
#
# # Use the parameter "convert_unicode=True" in create_engine if you need it
# core_db.engine = create_engine(DATABASE_URL, pool_size=10)
# core_db.session = scoped_session(sessionmaker(bind=core_db.engine))
# core_db.Base.query = core_db.session.query_property()

# Clear the DB
db.Base.metadata.drop_all(bind=db.engine)
print("Done")

