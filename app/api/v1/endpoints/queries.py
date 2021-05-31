from typing import Any
from fastapi import APIRouter, Depends
from py2neo import Graph

from app.db.db_connection import get_db
# from app.models.models import

router = APIRouter()


@router.get('/query-1', response_model=Any)
def query_1(author: str, db: Graph = Depends(get_db)) -> Any:
    query = "MATCH (a:Author{name: $name})-[:CONTRIBUTED]->(n) " \
            "RETURN n.title, n.year " \
            "ORDER BY n.year DESC"
    result = db.run(query, parameters={'name': author}).data()
    return result


@router.get('/query-2', response_model=Any)
def query_2(author: str, year: str, db: Graph = Depends(get_db)) -> Any:
    query = "MATCH (a:Author{name: $name})-[r_1:CONTRIBUTED]->(n{year: $year})<-[r_2:CONTRIBUTED]-(a_t:Author)" \
            "WHERE r_1.start_page = r_2.start_page " \
            "AND r_1.end_page = r_2.end_page " \
            "RETURN a_t.name as co_author, count(*) AS num_of_coauthorships " \
            "ORDER BY num_of_coauthorships DESC"
    result = db.run(query, parameters={'name': author, 'year': year}).data()
    return result


@router.get('/query-3', response_model=Any)
def query_3(limit: int, inproc: bool = True, db: Graph = Depends(get_db)) -> Any:
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


@router.get('/query-4', response_model=Any)
def query_4(limit: int, db: Graph = Depends(get_db)) -> Any:
    query = "MATCH (a1:Author)-[r1:CONTRIBUTED]->(publication)<-[r2:CONTRIBUTED]-(a2:Author) " \
            "WHERE a1 <> a2 " \
            "AND r1.start_page = r2.start_page " \
            "AND r1.end_page = r2.end_page " \
            "AND r1.first_author = True " \
            "WITH a1.name AS author_name, count(a2) AS num_of_coauthors " \
            "RETURN author_name, num_of_coauthors " \
            "ORDER BY num_of_coauthors DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-5', response_model=Any)
def query_5(year: str, limit: int, db: Graph = Depends(get_db)) -> Any:
    query = "MATCH (a1:Author)-[r1:CONTRIBUTED]->(n{year: $year})<-[r2:CONTRIBUTED]-(a2:Author) " \
            "WHERE a1 <> a2 " \
            "AND r1.start_page = r2.start_page " \
            "AND r1.end_page = r2.end_page " \
            "RETURN a1.name AS name, COUNT(a2) AS count " \
            "ORDER BY count DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'year': year, 'limit': limit}).data()
    return result


@router.get('/query-6', response_model=Any)
def query_6(limit: int, db: Graph = Depends(get_db)) -> Any:
    query = "MATCH (a1:Author)-[:CONTRIBUTED]->(n) " \
            "RETURN a1.name AS name, count(distinct(n.year)) AS count " \
            "ORDER BY count DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-7', response_model=Any)
def query_7(limit: int, db: Graph = Depends(get_db)) -> Any:
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


@router.get('/query-8', response_model=Any)
def query_8(limit: int, db: Graph = Depends(get_db)) -> Any:
    query = "MATCH (a1:Author)-[:CONTRIBUTED]->(n) " \
            "WITH a1, COUNT(DISTINCT(n.year)) AS activeYears, COUNT(n.title) AS publications " \
            "RETURN a1.name AS name, toFloat(publications) / activeYears AS count " \
            "ORDER BY count DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-9', response_model=Any)
def query_9(limit: int, db: Graph = Depends(get_db)) -> Any:
    query = "MATCH (a1:Author)-[r1:CONTRIBUTED]->()<-[r2:CONTRIBUTED]-(a2:Author) " \
            "WHERE a1 <> a2 " \
            "AND r1.start_page = r2.start_page " \
            "AND r1.end_page = r2.end_page " \
            "WITH a1 AS author, a2 AS coAuthor " \
            "MATCH (coAuthor:Author)-[r1:CONTRIBUTED]->()<-[r2:CONTRIBUTED]-(coAuthor_coAuthor:Author) " \
            "WHERE coAuthor <> coAuthor_coAuthor " \
            "AND author <> coAuthor_coAuthor " \
            "AND r1.start_page = r2.start_page " \
            "AND r1.end_page = r2.end_page " \
            "WITH author, coAuthor_coAuthor " \
            "WHERE NOT EXISTS {" \
            "   MATCH (author:Author)-[rr1:CONTRIBUTED]->()<-[rr2:CONTRIBUTED]-(coAuthor_coAuthor:Author) " \
            "   WHERE author <> coAuthor_coAuthor " \
            "   AND rr1.start_page = rr2.start_page " \
            "   AND rr1.end_page = rr2.end_page " \
            "} " \
            "RETURN author.name, COUNT(DISTINCT coAuthor_coAuthor) " \
            "ORDER BY COUNT(DISTINCT coAuthor_coAuthor) DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result
# 9
# MATCH (a1:Author)-[r1:CONTRIBUTED]->()<-[r2:CONTRIBUTED]-(a2:Author)
# WHERE a1 <> a2
# and r1.start_page = r2.start_page
# and r1.end_page = r2.end_page
# WITH a1 as author, a2 as coAuthor
# MATCH (coAuthor:Author)-[r1:CONTRIBUTED]->()<-[r2:CONTRIBUTED]-(coAuthor_coAuthor:Author)
# WHERE coAuthor <> coAuthor_coAuthor
# and author <> coAuthor_coAuthor
# and r1.start_page = r2.start_page
# and r1.end_page = r2.end_page
# with author, coAuthor_coAuthor
# where not exists {
#     MATCH (author:Author)-[rr1:CONTRIBUTED]->()<-[rr2:CONTRIBUTED]-(coAuthor_coAuthor:Author)
#     WHERE author <> coAuthor_coAuthor
#     and rr1.start_page = rr2.start_page
#     and rr1.end_page = rr2.end_page
# }
# return author.name, count(distinct coAuthor_coAuthor)
# order by count(distinct coAuthor_coAuthor) desc
# limit 10


@router.get('/query-10', response_model=Any)
def query_10(year: str, limit: int, db: Graph = Depends(get_db)) -> Any:
    query = "MATCH (a1:Author)-[:CONTRIBUTED]->(n{year: $year}) " \
            "WITH a1, COUNT(n.title) AS count " \
            "WHERE count > 3 " \
            "RETURN a1.name AS name, count " \
            "ORDER BY count DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'year': year, 'limit': limit}).data()
    return result


@router.get('/query-11', response_model=Any)
def query_11(author: str, year: str, db: Graph = Depends(get_db)) -> Any:
    query = "MATCH (a:Author{name: $name})-[r:CONTRIBUTED]->(n{year: $year}) " \
            "RETURN SUM(r.total_pages) AS total_pages"
    result = db.run(query, parameters={'name': author, 'year': year}).data()
    return result


@router.get('/query-12', response_model=Any)
def query_12(title: str, year: str, limit: int, first_author: bool = True, db: Graph = Depends(get_db)) -> Any:
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


@router.get('/query-13', response_model=Any)
def query_13(title: str, limit: int, db: Graph = Depends(get_db)) -> Any:
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
            "RETURN a1.name, a2.name, a3.name, count(ar) AS count " \
            "ORDER BY count DESC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'title': title, 'limit': limit}).data()
    return result


@router.get('/query-14', response_model=Any)
def query_14(limit: int, db: Graph = Depends(get_db)) -> Any:
    query = "MATCH (a1:Author)-[r1:CONTRIBUTED]->(:Incollection)-[:PUBLISHED]->(b:Book)<-[:PUBLISHED]-" \
            "(:Incollection)<-[r2:CONTRIBUTED]-(a2:Author) " \
            "WHERE id(a1) < id(a2) " \
            "AND r1.start_page <> r2.start_page " \
            "AND r1.end_page <> r2.end_page " \
            "WITH a1, a2 " \
            "WHERE NOT EXISTS { " \
            "   MATCH (a1)-[r1:CONTRIBUTED]->()<-[r2:CONTRIBUTED]->(a2) " \
            "   WHERE a1 <> a2 " \
            "   AND r1.start_page = r2.start_page " \
            "   AND r1.end_page = r2.end_page " \
            "} " \
            "RETURN a1.name, a2.name " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-15', response_model=Any)
def query_15(k: int, limit: int, db: Graph = Depends(get_db)) -> Any:
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


@router.get('/query-16', response_model=Any)
def query_16(limit: int, db: Graph = Depends(get_db)) -> Any:
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


@router.get('/query-17', response_model=Any)
def query_17(limit: int, db: Graph = Depends(get_db)) -> Any:
    query = "MATCH (a1:Author)-[:CONTRIBUTED]->(n) " \
            "WITH DISTINCT a1 AS a1, COLLECT(DISTINCT n.year) AS years " \
            "WITH a1, apoc.convert.toIntList(years) AS years " \
            "WITH a1, apoc.coll.sort(years) AS years " \
            "WITH a1, apoc.coll.pairsMin(years) AS years " \
            "WITH a1, REDUCE(output = [], r IN years | output + (r[1] - r[0])) AS years_differences " \
            "WHERE ANY(year IN years_differences WHERE year >= 2) " \
            "RETURN a1.name AS name, years_differences " \
            "ORDER BY years_differences ASC " \
            "LIMIT $limit"
    result = db.run(query, parameters={'limit': limit}).data()
    return result


@router.get('/query-18', response_model=Any)
def query_18(db: Graph = Depends(get_db)) -> Any:
    query = "MATCH (a1:Author)-[r:CONTRIBUTED]->(:Incollection)-[:PUBLISHED]->(b:Book) " \
            "RETURN a1.name, b.title, COUNT(r) AS parts " \
            "ORDER BY parts DESC " \
            "LIMIT 1"
    result = db.run(query).data()
    return result
