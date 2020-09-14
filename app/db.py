import os

import sqlalchemy
from databases import Database
from sqlalchemy import Column, Integer, MetaData, String, create_engine

DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1/realworld"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# SQLAlchemy
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# databases query builder
database = Database(DATABASE_URL)

users = sqlalchemy.Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("username", String, index=True),
    Column("email", String, unique=True, index=True, nullable=False),
    Column("bio", String, index=True),
    Column("image", String, nullable=True),
    Column("hashed_password", String, nullable=False),
)
