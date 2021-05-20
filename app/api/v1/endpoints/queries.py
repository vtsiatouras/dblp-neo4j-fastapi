from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from py2neo import Graph
from datetime import datetime, timedelta

from app.db.db_connection import get_db
# from app.models.models import

router = APIRouter()


@router.get('/test', response_model=Any)
def test(db: Graph = Depends(get_db)) -> Any:
    print(db.relationships)
