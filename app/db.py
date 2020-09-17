import sqlalchemy
from databases import Database
from sqlalchemy import Column, Integer, MetaData, String, create_engine

from app.core.config import settings

# SQLAlchemy
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
metadata = MetaData()

# databases query builder
database = Database(settings.SQLALCHEMY_DATABASE_URI)

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
