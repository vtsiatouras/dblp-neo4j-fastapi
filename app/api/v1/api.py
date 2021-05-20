from fastapi import APIRouter

from app.api.v1.endpoints import queries

api_router = APIRouter()
api_router.include_router(queries.router, tags=['queries'])

