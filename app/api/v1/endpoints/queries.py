from typing import Any, List
from fastapi import APIRouter, Depends
from py2neo import Graph

from app.db.db_connection import get_db
from app.models.models import NameCount, TitleYear, TotalPages, NamesCount, NamesPair, NameConsecutiveYears, \
    NameAverageAuthors, NameConsecutiveYearsDifferences, NameBookParts

router = APIRouter()


@router.get('/query-1', response_model=List[TitleYear])
def query_1(author: str, db: Graph = Depends(get_db)) -> Any:
    """Find the titles (title, year) of publications that a particular author has published.
    """
    query = "MATCH (a:Author{name: $name})-[:CONTRIBUTED]->(n) " \
            "RETURN n.title AS title, n.year AS year " \
            "ORDER BY year DESC"
    result = db.run(query, parameters={'name': author}).data()
    return result


@router.get('/query-2', response_model=List[NameCount])
def query_2(author: str, year: str, db: Graph = Depends(get_db)) -> Any:
    """Find the co-authors of an author (name, number of co-authorships) for a particular year.
    """
    query = "MATCH (a1:Author{name: $name})-[r1:CONTRIBUTED]->(n{year: $year})<-[r2:CONTRIBUTED]-(a2:Author)" \
            "WHERE r1.start_page = r2.start_page " \
            "AND r1.end_page = r2.end_page " \
            "RETURN a2.name as name, count(*) AS count " \
            "ORDER BY count DESC"
    result = db.run(query, parameters={'name': author, 'year': year}).data()
    return result


@router.get('/query-3', response_model=List[NameCount])
def query_3(limit: int, inproc: bool = True, db: Graph = Depends(get_db)) -> Any:
    """Find the top-K authors (name, count) with regard to most conference/journal publications.
    """
    if inproc:
        query = "MATCH (a:Author)-[r:CONTRIBUTED]->(n:Inproceedings) " \
                "RETURN a.name AS name, COUNT(n) AS count " \
                "ORDER BY count DESC " \
                "LIMIT $limit"
    else:
        query = "MATCH (a:Author)-[r:CONTRIBUTED]->(n:Article) " \
                "RETURN a.name AS name, COUNT(n) AS count " \
                "ORDER BY count DESC " \
                "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-4', response_model=List[NameCount])
def query_4(limit: int, db: Graph = Depends(get_db)) -> Any:
    """Find the top-K authors (name, count) with regard to most co-authors in a single work.
    """
    query = "MATCH (a1:Author)-[r1:CONTRIBUTED]->()<-[r2:CONTRIBUTED]-(a2:Author) " \
            "WHERE a1 <> a2 " \
            "AND r1.start_page = r2.start_page " \
            "AND r1.end_page = r2.end_page " \
            "AND r1.first_author = True " \
            "RETURN a1.name AS name, count(a2) AS count " \
            "ORDER BY count DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-5', response_model=List[NameCount])
def query_5(year: str, limit: int, db: Graph = Depends(get_db)) -> Any:
    """Find the top-K authors (name, count) with regard to most co-authors in a particular year.
    """
    query = "MATCH (a1:Author)-[r1:CONTRIBUTED]->(n{year: $year})<-[r2:CONTRIBUTED]-(a2:Author) " \
            "WHERE a1 <> a2 " \
            "AND r1.start_page = r2.start_page " \
            "AND r1.end_page = r2.end_page " \
            "RETURN a1.name AS name, COUNT(a2) AS count " \
            "ORDER BY count DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'year': year, 'limit': limit}).data()
    return result


@router.get('/query-6', response_model=List[NameCount])
def query_6(limit: int, db: Graph = Depends(get_db)) -> Any:
    """Find the top-K authors (name, count) with regard to most active years.
    """
    query = "MATCH (a:Author)-[:CONTRIBUTED]->(n) " \
            "RETURN a.name AS name, count(distinct(n.year)) AS count " \
            "ORDER BY count DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-7', response_model=List[NameCount])
def query_7(limit: int, db: Graph = Depends(get_db)) -> Any:
    """Find the top-K authors (name, count) with regard to most distinct pairs of co-authors that have not published
    together.
    """
    query = "MATCH (a1:Author)-[r1:CONTRIBUTED]->()<-[r2:CONTRIBUTED]-(a2:Author) " \
            "WHERE a1 <> a2 " \
            "AND r1.start_page = r2.start_page " \
            "AND r1.end_page = r2.end_page " \
            "WITH a1 AS author, COLLECT(DISTINCT(a2)) AS coAuthors1, COLLECT(DISTINCT(a2)) AS coAuthors2 " \
            "UNWIND coAuthors1 AS coAuthor1 " \
            "UNWIND coAuthors2 AS coAuthor2 " \
            "MATCH (coAuthor1)-[r3:CONTRIBUTED]->(n)<-[r4:CONTRIBUTED]-(coAuthor2) " \
            "WHERE id(coAuthor1) < id(coAuthor2) " \
            "AND r3.start_page = r3.start_page " \
            "AND r4.end_page = r4.end_page " \
            "WITH coAuthors1, author, coAuthor1, coAuthor2, COUNT(*) AS worked " \
            "RETURN author.name AS name, SIZE(coAuthors1)^2 - COUNT(*) AS count " \
            "ORDER BY count DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-8', response_model=List[NameCount])
def query_8(limit: int, db: Graph = Depends(get_db)) -> Any:
    """Find the top-K authors (name, count) with regard to largest average number of journal publications per year
    (consider only active years).
    """
    query = "MATCH (a:Author)-[:CONTRIBUTED]->(n) " \
            "WITH a, COUNT(DISTINCT(n.year)) AS activeYears, COUNT(n.title) AS publications " \
            "RETURN a.name AS name, toFloat(publications) / activeYears AS count " \
            "ORDER BY count DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-9', response_model=List[NameCount])
def query_9(limit: int, db: Graph = Depends(get_db)) -> Any:
    """Find the top-K authors (name, count) that a given author has not worked with, with regard
    to most co-authorships with authors that the given author has worked with.
    """
    query = "MATCH (a1:Author)-[r1:CONTRIBUTED]->(work1)<-[r2_1:CONTRIBUTED]-(a2:Author)-[r2_2:CONTRIBUTED]->" \
            "(work2)<-[r3:CONTRIBUTED]-(a3:Author) " \
            "WHERE work1 <> work2 " \
            "AND a1 <> a2 " \
            "AND a2 <> a3 " \
            "AND a3 <> a1 " \
            "AND r1.start_page = r2_1.start_page " \
            "AND r1.end_page = r2_1.end_page " \
            "AND r2_2.start_page = r3.start_page " \
            "AND r2_2.end_page = r3.end_page " \
            "WITH a1, a3 " \
            "OPTIONAL MATCH (a1)-[rr1:CONTRIBUTED]->(work)<-[rr2:CONTRIBUTED]-(a3) " \
            "WHERE a1 <> a3 " \
            "AND rr1.start_page = rr2.start_page " \
            "AND rr1.end_page = rr2.end_page " \
            "WITH a1, a3, work " \
            "WHERE work IS NULL " \
            "RETURN a1.name AS name, COUNT(DISTINCT a3) AS count " \
            "ORDER BY count DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-10', response_model=List[NameCount])
def query_10(year: str, limit: int, db: Graph = Depends(get_db)) -> Any:
    """Find the authors (name, count) that have published more than three works in a given single year.
    """
    query = "MATCH (a:Author)-[:CONTRIBUTED]->(n{year: $year}) " \
            "WITH a, COUNT(n.title) AS count " \
            "WHERE count > 3 " \
            "RETURN a.name AS name, count " \
            "ORDER BY count DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'year': year, 'limit': limit}).data()
    return result


@router.get('/query-11', response_model=List[TotalPages])
def query_11(author: str, year: str, db: Graph = Depends(get_db)) -> Any:
    """Find the number of pages that a particular author has published in a given year.
    """
    query = "MATCH (a:Author{name: $name})-[r:CONTRIBUTED]->(n{year: $year}) " \
            "RETURN SUM(r.total_pages) AS total_pages"
    result = db.run(query, parameters={'name': author, 'year': year}).data()
    return result


@router.get('/query-12', response_model=List[NameCount])
def query_12(title: str, year: str, limit: int, first_author: bool = True, db: Graph = Depends(get_db)) -> Any:
    """Find the top-K authors (name, count) with regard to articles published in a particular journal
    as a first/last author in a given year.
    """
    if first_author:
        query = "MATCH (a:Author)-[r:CONTRIBUTED{first_author: True}]->(ar:Article{year: $year})-[:PUBLISHED]->" \
                "(j:Journal{title: $title}) " \
                "RETURN a.name AS name, COUNT(ar) AS count " \
                "ORDER BY count DESC " \
                "LIMIT $limit"
    else:
        query = "MATCH (a:Author)-[r:CONTRIBUTED{last_author: True}]->(ar:Article{year: $year})-[:PUBLISHED]->" \
                "(j:Journal{title: $title}) " \
                "RETURN a.name AS name, COUNT(ar) AS count " \
                "ORDER BY count DESC " \
                "LIMIT $limit"
    result = db.run(query, parameters={'title': title, 'year': year, 'limit': limit}).data()
    return result


@router.get('/query-13', response_model=List[NamesCount])
def query_13(title: str, limit: int, db: Graph = Depends(get_db)) -> Any:
    """Find the three authors that have appeared as co-authors for the most times in a particular journal.
    """
    query = "MATCH (a1:Author)-[r1:CONTRIBUTED]->(ar:Article)-[:PUBLISHED]->(j:Journal{title: $title}) " \
            "MATCH (a2:Author)-[r2:CONTRIBUTED]->(ar:Article)-[:PUBLISHED]->(j:Journal{title: $title}) " \
            "MATCH (a3:Author)-[r3:CONTRIBUTED]->(ar:Article)-[:PUBLISHED]->(j:Journal{title: $title}) " \
            "WHERE id(a1) < id(a2) < id(a3) " \
            "AND r1.start_page = r2.start_page " \
            "AND r1.end_page = r2.end_page " \
            "AND r3.start_page = r2.start_page " \
            "AND r3.end_page = r2.end_page " \
            "AND r1.start_page = r3.start_page " \
            "AND r1.end_page = r3.end_page " \
            "RETURN a1.name AS name1, a2.name AS name2, a3.name AS name3, count(ar) AS count " \
            "ORDER BY count DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'title': title, 'limit': limit}).data()
    return result


@router.get('/query-14', response_model=List[NamesPair])
def query_14(limit: int, db: Graph = Depends(get_db)) -> Any:
    """Find pairs of authors that have appeared in different parts of the same book and have never co-authored a work.
    """
    query = "MATCH (a1:Author)-[r1:CONTRIBUTED]->(:Incollection)-[:PUBLISHED]->(b:Book)<-" \
            "[:PUBLISHED]-(:Incollection)<-[r2:CONTRIBUTED]-(a2:Author) " \
            "WHERE id(a1) < id(a2) " \
            "AND r1.start_page <> r2.start_page " \
            "AND r1.end_page <> r2.end_page " \
            "WITH a1, a2 " \
            "OPTIONAL MATCH (a1)-[r1:CONTRIBUTED]->(work)<-[r2:CONTRIBUTED]-(a2) " \
            "WHERE a1 <> a2 " \
            "AND r1.start_page = r2.start_page " \
            "AND r1.end_page = r2.end_page " \
            "WITH a1, a2, work " \
            "WHERE work IS NULL " \
            "RETURN DISTINCT a1.name AS name1, a2.name AS name2 " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-15', response_model=List[NameConsecutiveYears])
def query_15(k: int, limit: int, db: Graph = Depends(get_db)) -> Any:
    """Find the authors that have published work for K consecutive years.
    """
    query = "MATCH (a1:Author)-[:CONTRIBUTED]->(n) " \
            "WITH a1, COLLECT(DISTINCT n.year) AS years " \
            "WITH a1, apoc.convert.toIntList(years) AS years " \
            "WITH a1, apoc.coll.sort(years) AS years " \
            "WITH a1, apoc.coll.pairsMin(years) AS years " \
            "WITH a1, REDUCE(output = [], r IN years | output + (r[1] - r[0])) AS years " \
            "WITH a1, apoc.agg.maxItems(years, size(years), 1) AS consecutiveYears " \
            "WITH a1, consecutiveYears.value AS consecutiveYears " \
            "WHERE consecutiveYears = $k " \
            "RETURN a1.name AS name, consecutiveYears " \
            "LIMIT $limit"
    result = db.run(query, parameters={'k': k, 'limit': limit}).data()
    return result


@router.get('/query-16', response_model=List[NameAverageAuthors])
def query_16(limit: int, db: Graph = Depends(get_db)) -> Any:
    """Find the top-K authors with regard to average number of co-authors in their publications.
    """
    query = "MATCH (a1:Author)-[r1:CONTRIBUTED]->(n)<-[r2:CONTRIBUTED]-(a2:Author) " \
            "WHERE id(a1) < id(a2) " \
            "AND r1.start_page = r2.start_page " \
            "AND r1.end_page = r2.end_page " \
            "WITH a1, COLLECT(a2) AS coAuthors, COLLECT(DISTINCT n) AS publications " \
            "RETURN a1.name AS name, toFloat(SIZE(coAuthors)) / toFloat(SIZE(publications)) AS averageCoAuthors " \
            "ORDER BY averageCoAuthors DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-17', response_model=List[NameConsecutiveYearsDifferences])
def query_17(limit: int, db: Graph = Depends(get_db)) -> Any:
    """Find the authors of consecutively published papers with more than a given amount of years between them.
    """
    query = "MATCH (a1:Author)-[:CONTRIBUTED]->(n) " \
            "WITH DISTINCT a1 AS a1, COLLECT(DISTINCT n.year) AS years " \
            "WITH a1, apoc.convert.toIntList(years) AS years " \
            "WITH a1, apoc.coll.sort(years) AS years " \
            "WITH a1, apoc.coll.pairsMin(years) AS years " \
            "WITH a1, REDUCE(output = [], r IN years | output + (r[1] - r[0])) AS yearsDifferences " \
            "WHERE ANY(year IN yearsDifferences WHERE year >= 2) " \
            "RETURN a1.name AS name, yearsDifferences " \
            "ORDER BY yearsDifferences ASC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-18', response_model=List[NameBookParts])
def query_18(db: Graph = Depends(get_db)) -> Any:
    """Find the author (name, count) with the most parts in a single book of collective works.
    """
    query = "MATCH (a1:Author)-[r:CONTRIBUTED]->(:Incollection)-[:PUBLISHED]->(b:Book) " \
            "RETURN a1.name AS name, b.title AS title, COUNT(r) AS parts " \
            "ORDER BY parts DESC " \
            "LIMIT 1"
    result = db.run(query).data()
    return result
