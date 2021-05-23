import gzip
import os
import time

from lxml import etree
from argparse import ArgumentParser
from py2neo.bulk import create_nodes, create_relationships
from itertools import islice

from app.db.db_connection import get_db

parser = ArgumentParser()
parser.add_argument("-f", nargs="+", help="The input file to parse")
parser.add_argument("-dtd", nargs="+", help="The DTD file")

args = parser.parse_args()
start = time.time()

authors_data = []
articles_data = []
inproceedings_data = []
incollection_data = []
book_data = []
articles_relations_data = []
inproceedings_relations_data = []
incollection_relations_data = []
inproceedings_book_relations_data = []
incollection_book_relations_data = []

authors_names_set = set()
articles_titles_set = set()
inproceedings_titles_set = set()
incollection_titles_set = set()
book_titles_set = set()


def clean_database():
    # Get database connection
    graph_db = next(get_db())
    graph_db.delete_all()


def create_indices():
    # Get database connection
    graph_db = next(get_db())
    graph_db.run("CREATE INDEX AuthorNameIndex IF NOT EXISTS FOR (t:Author) ON (t.name)")
    graph_db.run("CREATE INDEX ArticleTitleIndex IF NOT EXISTS FOR (t:Article) ON (t.title)")
    graph_db.run("CREATE INDEX InproceedingsTitleIndex IF NOT EXISTS FOR (t:Inproceedings) ON (t.title)")
    graph_db.run("CREATE INDEX IncollectionTitleIndex IF NOT EXISTS FOR (t:Incollection) ON (t.title)")
    graph_db.run("CREATE INDEX BookTitleIndex IF NOT EXISTS FOR (t:Book) ON (t.title)")


def seed_database():
    # Get database connection
    graph_db = next(get_db())

    batch_size = 5000
    authors_iter = iter(authors_data)
    articles_iter = iter(articles_data)
    inproceedings_iter = iter(inproceedings_data)
    incollection_iter = iter(incollection_data)
    book_iter = iter(book_data)
    articles_relations_iter = iter(articles_relations_data)
    inproceedings_relations_iter = iter(inproceedings_relations_data)
    incollection_relations_iter = iter(incollection_relations_data)
    inproceedings_book_relations_iter = iter(inproceedings_book_relations_data)
    incollection_book_relations_iter = iter(incollection_book_relations_data)

    while True:
        authors_data_batch = list(islice(authors_iter, batch_size))
        articles_data_batch = list(islice(articles_iter, batch_size))
        inproceedings_data_batch = list(islice(inproceedings_iter, batch_size))
        incollection_data_batch = list(islice(incollection_iter, batch_size))
        book_data_batch = list(islice(book_iter, batch_size))

        articles_relations_data_batch = list(islice(articles_relations_iter, batch_size))
        inproceedings_relations_data_batch = list(islice(inproceedings_relations_iter, batch_size))
        incollection_relations_data_batch = list(islice(incollection_relations_iter, batch_size))

        inproceedings_book_relations_data_batch = list(islice(inproceedings_book_relations_iter, batch_size))
        incollection_book_relations_data_batch = list(islice(incollection_book_relations_iter, batch_size))

        if authors_data_batch:
            create_nodes(graph_db.auto(), data=authors_data_batch, labels={"Author"})
        if articles_data_batch:
            create_nodes(graph_db.auto(), data=articles_data_batch, labels={"Article"})
        if inproceedings_data_batch:
            create_nodes(graph_db.auto(), data=inproceedings_data_batch, labels={"Inproceedings"})
        if incollection_data_batch:
            create_nodes(graph_db.auto(), data=incollection_data_batch, labels={"Incollection"})
        if book_data_batch:
            create_nodes(graph_db.auto(), data=book_data_batch, labels={"Book"})
        if articles_relations_data_batch:
            create_relationships(graph_db.auto(), data=articles_relations_data_batch, rel_type="CONTRIBUTED",
                                 start_node_key=("Author", "name"), end_node_key=("Article", "title"))
        if inproceedings_relations_data_batch:
            create_relationships(graph_db.auto(), data=inproceedings_relations_data_batch, rel_type="CONTRIBUTED",
                                 start_node_key=("Author", "name"), end_node_key=("Inproceedings", "title"))
        if inproceedings_book_relations_data_batch:
            create_relationships(graph_db.auto(), data=inproceedings_book_relations_data_batch, rel_type="WROTE",
                                 start_node_key=("Inproceedings", "title"), end_node_key=("Book", "title"))
        if incollection_relations_data_batch:
            create_relationships(graph_db.auto(), data=incollection_book_relations_data_batch, rel_type="WROTE",
                                 start_node_key=("Incollection", "title"), end_node_key=("Book", "title"))

        if not any([authors_data_batch, articles_data_batch, inproceedings_data_batch, incollection_data_batch,
                    book_data_batch, articles_relations_data_batch, inproceedings_relations_data_batch,
                    incollection_relations_data_batch, inproceedings_book_relations_data_batch,
                    incollection_book_relations_data_batch]):
            break


def import_data(article_xml: str, dtd_file: str) -> None:
    # Parse xml element
    dtd_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), dtd_file)
    dtd = f"<!DOCTYPE dblp SYSTEM '{dtd_path}'>"
    xml = dtd + article_xml
    parser = etree.XMLParser(load_dtd=True)
    tree = etree.fromstring(xml, parser=parser)

    authors = tree.xpath("//author")
    authors_names = []
    for author in authors:
        author_dict = {"name": author.text}
        authors_names.append(author.text)
        if author.text not in authors_names_set:
            authors_names_set.add(author.text)
            authors_data.append(author_dict)

    title = tree.xpath("//title")
    year = tree.xpath("//year")

    if tree.tag == "article":
        journal = tree.xpath("//journal")
        if title and journal and year:
            article_dict = {"title": title[0].text, "journal": journal[0].text, "year": year[0].text}
            if title[0].text not in articles_titles_set:
                articles_titles_set.add(title[0].text)
                articles_data.append(article_dict)

            for author_name in authors_names:
                articles_relations_data.append((author_name, {}, title[0].text))

    elif tree.tag == "inproceedings":
        booktitle = tree.xpath("//booktitle")
        pages = tree.xpath("//pages")
        if title and booktitle and year and pages:
            inproceedings_dict = {"title": title[0].text, "booktitle": booktitle[0].text, "year": year[0].text}
            if title[0].text not in inproceedings_titles_set:
                inproceedings_titles_set.add(title[0].text)
                inproceedings_data.append(inproceedings_dict)

            if booktitle[0].text not in book_titles_set:
                book_titles_set.add(booktitle[0].text)
                book_data.append({'title': booktitle[0].text})
                inproceedings_book_relations_data.append((title[0].text, {'pages': pages[0].text}, booktitle[0].text))

            for author_name in authors_names:
                inproceedings_relations_data.append((author_name, {}, title[0].text))

    elif tree.tag == "incollection":
        booktitle = tree.xpath("//booktitle")
        publisher = tree.xpath("//publisher")
        pages = tree.xpath("//pages")
        if title and booktitle and year and publisher and pages:
            incollection_dict = {"title": title[0].text, "booktitle": booktitle[0].text, "year": year[0].text,
                                 "publisher": publisher[0].text}
            if title[0].text not in incollection_titles_set:
                incollection_titles_set.add(title[0].text)
                incollection_data.append(incollection_dict)

            if booktitle[0].text not in book_titles_set:
                book_titles_set.add(booktitle[0].text)
                book_data.append({'title': booktitle[0].text})
                incollection_book_relations_data.append((title[0].text, {'pages': pages[0].text}, booktitle[0].text))

            for author_name in authors_names:
                incollection_relations_data.append((author_name, {}, title[0].text))


def parse_xml_gz_file(input_file: str, dtd_file: str) -> None:
    open_tags = ["<article", "<inproceedings", "<incollection"]
    close_tags = ["</article>", "</inproceedings>", "</incollection>"]

    count = 1

    with gzip.open(input_file, "rt") as f:
        extract = False
        buffer = ""

        for line in f:

            for tag in close_tags:
                if tag in line:
                    extract = False
                    idx = line.index(tag)
                    buffer += line[:idx] + tag
                    import_data(buffer, dtd_file)
                    print(count)
                    count += 1
                    buffer = ""
                    break

            for tag in open_tags:
                if tag in line:
                    idx = line.index(tag)
                    line = line[idx:]
                    extract = True
                    break

            if extract:
                buffer += str(line)


for input_file in args.f:
    print(f"Processing file {input_file}")
    if input_file.endswith("dblp.xml.gz"):
        clean_database()
        create_indices()
        parse_xml_gz_file(input_file=input_file, dtd_file=args.dtd[0])
        seed_database()
    else:
        print(f"File '{input_file}' cannot be processed, skipping.")

end = time.time()
print(f"Finished importing dataset, took {(end - start):.2f} seconds")
