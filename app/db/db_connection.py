from py2neo import Graph

from app.core.config import settings


def get_db():
    yield Graph(password=settings.DB_PASSWORD)
