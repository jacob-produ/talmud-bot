import os
from school_manager.constants import constants
from core import utils
from sqlalchemy import create_engine
# noinspection PyUnresolvedReferences
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
# noinspection PyUnresolvedReferences
from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, Float, UniqueConstraint, CheckConstraint

# Create DB session

if os.name == 'nt':
    DB_IP_ADDR = constants.DEFAULT_IP_ADDRESS
else:
    DB_IP_ADDR = "127.0.0.1"

DATABASE_URL = f'mysql+mysqldb://school_manager:ZSchoolManager116!Z@{DB_IP_ADDR}/school_manager?charset=utf8'

# Use the parameter "convert_unicode=True" in create_engine if you need it
engine = create_engine(DATABASE_URL, pool_size=10)
session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = session.query_property()