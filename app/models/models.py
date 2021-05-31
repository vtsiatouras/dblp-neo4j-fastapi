from pydantic import BaseModel
from typing import List


class NameCount(BaseModel):
    name: str
    count: int


class NameConsecutiveYears(BaseModel):
    name: str
    consecutiveYears: int


class NameConsecutiveYearsDifferences(BaseModel):
    name: str
    yearsDifferences: List[int]


class NameAverageAuthors(BaseModel):
    name: str
    averageCoAuthors: float


class NameBookParts(BaseModel):
    name: str
    title: str
    parts: int


class NamesCount(BaseModel):
    name1: str
    name2: str
    name3: str
    count: int


class NamesPair(BaseModel):
    name1: str
    name2: str


class TitleYear(BaseModel):
    title: str
    year: int


class TotalPages(BaseModel):
    total_pages: int
