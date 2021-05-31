from py2neo import Graph

from app.core.config import settings


def get_db():
    yield Graph(host=settings.DB_HOST, password=settings.DB_PASSWORD)
