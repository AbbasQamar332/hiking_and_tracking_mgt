# from collections.abc import Generator
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()


# def _build_database_url() -> str:
#     # If a full DATABASE_URL is provided in .env, use it directly
#     explicit_url = os.getenv("DATABASE_URL")
#     if explicit_url:
#         return explicit_url

#     # Otherwise, grab individual components with clean fallbacks
#     user = os.getenv("MYSQL_USER", "root")
#     password = os.getenv("MYSQL_PASSWORD", "")
#     host = os.getenv("MYSQL_HOST", "localhost")
#     port = os.getenv("MYSQL_PORT", "3306")
#     database = os.getenv("MYSQL_DATABASE", "hiking_management_system")

#     # Clean, easy-to-read standard connection string format
#     return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    url=SQLALCHEMY_DATABASE_URL
    )


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()