import gzip
import os
import re
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
article_data = []
inproceedings_data = []
incollection_data = []
journal_data = []
conference_data = []
book_data = []

authors_article_relations_data = []
authors_inproceedings_relations_data = []
authors_incollection_relations_data = []
article_journal_relations_data = []
inproceedings_conference_relations_data = []
incollection_book_relations_data = []

authors_names_set = set()
article_titles_set = set()
inproceedings_titles_set = set()
incollection_titles_set = set()
journal_titles_set = set()
conference_titles_set = set()
book_titles_set = set()


def clean_database() -> None:
    """Cleans up existing database
    :return: None
    """
    # Get database connection
    graph_db = next(get_db())
    graph_db.delete_all()


def create_constraints() -> None:
    """Creates required constraints in the database
    :return:
    """
    # Get database connection
    graph_db = next(get_db())
    graph_db.run("CREATE CONSTRAINT AuthorNameConstraint IF NOT EXISTS ON (n:Author) ASSERT n.name IS UNIQUE")
    graph_db.run("CREATE CONSTRAINT ArticleTitleConstraint IF NOT EXISTS ON (n:Article) ASSERT (n.title, n.year) "
                 "IS UNIQUE")
    graph_db.run("CREATE CONSTRAINT InproceedingsTitleConstraint IF NOT EXISTS ON (n:Inproceedings) "
                 "ASSERT (n.title, n.year) IS UNIQUE")
    graph_db.run("CREATE CONSTRAINT IncollectionTitleConstraint IF NOT EXISTS ON (n:Incollection) "
                 "ASSERT (n.title, n.year) IS UNIQUE")
    graph_db.run("CREATE CONSTRAINT JournalTitleConstraint IF NOT EXISTS ON (n:Article) ASSERT n.title IS UNIQUE")
    graph_db.run("CREATE CONSTRAINT ConferenceConstraint IF NOT EXISTS ON (n:Conference) ASSERT n.title IS UNIQUE")
    graph_db.run("CREATE CONSTRAINT BookTitleConstraint IF NOT EXISTS ON (n:Book) ASSERT n.title IS UNIQUE")


def create_indices() -> None:
    """Creates required indices at the database
    :return: None
    """
    # Get database connection
    graph_db = next(get_db())
    graph_db.run("CREATE INDEX AuthorNameIndex IF NOT EXISTS FOR (t:Author) ON (t.name)")
    graph_db.run("CREATE INDEX ArticleTitleIndex IF NOT EXISTS FOR (t:Article) ON (t.title, t.year)")
    graph_db.run("CREATE INDEX InproceedingsTitleIndex IF NOT EXISTS FOR (t:Inproceedings) ON (t.title, t.year)")
    graph_db.run("CREATE INDEX IncollectionTitleIndex IF NOT EXISTS FOR (t:Incollection) ON (t.title, t.year)")
    graph_db.run("CREATE INDEX ArticleYearIndex IF NOT EXISTS FOR (t:Article) ON (t.year)")
    graph_db.run("CREATE INDEX InproceedingsYearIndex IF NOT EXISTS FOR (t:Inproceedings) ON (t.year)")
    graph_db.run("CREATE INDEX IncollectionYearIndex IF NOT EXISTS FOR (t:Incollection) ON (t.year)")
    graph_db.run("CREATE INDEX JournalTitleIndex IF NOT EXISTS FOR (t:Journal) ON (t.title)")
    graph_db.run("CREATE INDEX ConferenceIndex IF NOT EXISTS FOR (t:Conference) ON (t.title)")
    graph_db.run("CREATE INDEX BookTitleIndex IF NOT EXISTS FOR (t:Book) ON (t.title)")
    # graph_db.run("CALL db.index.fulltext.createRelationshipIndex(\"PagesIndex\", [\"WROTE\"], [\"pages\"])")
    # graph_db.run("CALL db.index.fulltext.createRelationshipIndex(\"TotalPagesIndex\", [\"WROTE\"], [\"total_pages\"])")


def seed_database() -> None:
    """Populates the database with the extracted data
    :return: None
    """
    # Get database connection
    graph_db = next(get_db())

    batch_size = 5000
    authors_iter = iter(authors_data)
    article_iter = iter(article_data)
    inproceedings_iter = iter(inproceedings_data)
    incollection_iter = iter(incollection_data)

    journal_iter = iter(journal_data)
    conference_iter = iter(conference_data)
    book_iter = iter(book_data)

    authors_articles_relations_iter = iter(authors_article_relations_data)
    authors_inproceedings_relations_iter = iter(authors_inproceedings_relations_data)
    authors_incollection_relations_iter = iter(authors_incollection_relations_data)

    article_journal_relations_iter = iter(article_journal_relations_data)
    inproceedings_conference_relations_iter = iter(inproceedings_conference_relations_data)
    incollection_book_relations_iter = iter(incollection_book_relations_data)

    # Insert all nodes first
    while True:
        authors_data_batch = list(islice(authors_iter, batch_size))
        articles_data_batch = list(islice(article_iter, batch_size))
        inproceedings_data_batch = list(islice(inproceedings_iter, batch_size))
        incollection_data_batch = list(islice(incollection_iter, batch_size))

        journal_data_batch = list(islice(journal_iter, batch_size))
        conference_data_batch = list(islice(conference_iter, batch_size))
        book_data_batch = list(islice(book_iter, batch_size))

        if authors_data_batch:
            create_nodes(graph_db.auto(), data=authors_data_batch, labels={"Author"})
        if articles_data_batch:
            create_nodes(graph_db.auto(), data=articles_data_batch, labels={"Article"})
        if inproceedings_data_batch:
            create_nodes(graph_db.auto(), data=inproceedings_data_batch, labels={"Inproceedings"})
        if incollection_data_batch:
            create_nodes(graph_db.auto(), data=incollection_data_batch, labels={"Incollection"})
        if journal_data_batch:
            create_nodes(graph_db.auto(), data=journal_data_batch, labels={"Journal"})
        if conference_data_batch:
            create_nodes(graph_db.auto(), data=conference_data_batch, labels={"Conference"})
        if book_data_batch:
            create_nodes(graph_db.auto(), data=book_data_batch, labels={"Book"})

        if not any([authors_data_batch, articles_data_batch, inproceedings_data_batch, incollection_data_batch,
                    journal_data_batch, conference_data_batch, book_data_batch]):
            break

    # Continue up with relationships
    while True:
        authors_articles_relations_data_batch = list(islice(authors_articles_relations_iter, batch_size))
        authors_inproceedings_relations_data_batch = list(islice(authors_inproceedings_relations_iter, batch_size))
        authors_incollection_relations_data_batch = list(islice(authors_incollection_relations_iter, batch_size))

        article_journal_relations_data_batch = list(islice(article_journal_relations_iter, batch_size))
        inproceedings_conference_relations_data_batch = \
            list(islice(inproceedings_conference_relations_iter, batch_size))
        incollection_book_relations_data_batch = list(islice(incollection_book_relations_iter, batch_size))

        if authors_articles_relations_data_batch:
            create_relationships(graph_db.auto(), authors_articles_relations_data_batch, "CONTRIBUTED",
                                 start_node_key=("Author", "name"), end_node_key=("Article", "title", "year"))
        if authors_inproceedings_relations_data_batch:
            create_relationships(graph_db.auto(), authors_inproceedings_relations_data_batch, "CONTRIBUTED",
                                 start_node_key=("Author", "name"), end_node_key=("Inproceedings", "title", "year"))
        if authors_incollection_relations_data_batch:
            create_relationships(graph_db.auto(), authors_incollection_relations_data_batch, "CONTRIBUTED",
                                 start_node_key=("Author", "name"), end_node_key=("Incollection", "title", "year"))
        if article_journal_relations_data_batch:
            create_relationships(graph_db.auto(), article_journal_relations_data_batch, "PUBLISHED",
                                 start_node_key=("Article", "title", "year"), end_node_key=("Journal", "title"))
        if inproceedings_conference_relations_data_batch:
            create_relationships(graph_db.auto(), inproceedings_conference_relations_data_batch, "PUBLISHED",
                                 start_node_key=("Inproceedings", "title", "year"),
                                 end_node_key=("Conference", "title"))
        if incollection_book_relations_data_batch:
            create_relationships(graph_db.auto(), incollection_book_relations_data_batch, "PUBLISHED",
                                 start_node_key=("Incollection", "title", "year"), end_node_key=("Book", "title"))

        if not any([authors_articles_relations_data_batch, authors_inproceedings_relations_data_batch,
                    authors_incollection_relations_data_batch, article_journal_relations_data_batch,
                    inproceedings_conference_relations_data_batch, incollection_book_relations_data_batch]):
            break


def extract_pages_info(pages: str) -> dict:
    """Extracts the total number of pages given string input in format <digit>-<digit>
    :param pages: The pages range
    :return: Tuple start_page, end_page, total_pages
    """
    pages_lst = re.findall(r"\d+", pages)
    if pages_lst:
        start_page = int(pages_lst[0])
        end_page = int(pages_lst[1]) if len(pages_lst) > 1 else int(pages_lst[0])
        return {"start_page": start_page,
                "end_page": end_page,
                "total_pages": abs(end_page - start_page) if len(pages_lst) > 1 else 1}
    else:
        return {}


def associate_authors_with_publications(authors_names: list,
                                        title: str,
                                        year: str,
                                        data_list: list,
                                        pages_dict: dict
                                        ) -> None:
    """Makes association list of authors with a publication
    :param authors_names: The names of the authors in list
    :param title: The title of the publication
    :param year: The year of the publication
    :param data_list: The list that contains existing relations in order to append a new one
    :param pages_dict: The pages dictionary
    :return: None
    """
    for it, author_name in enumerate(authors_names):
        rel_dict = pages_dict
        if it == 0:
            rel_dict.update({'first_author': True})
        if it == len(authors_names) - 1 and it != 0:
            rel_dict.update({'last_author': True})
        data_list.append((author_name, rel_dict, (title, year)))


def extract_authors(authors: list) -> list:
    """Extracts authors to data list in order to be stored in bulk insert and returns a list with their names
    :param authors: The authors list parsed from the XML
    :return: List of the names of the authors
    """
    authors_names = []
    for author in authors:
        author_dict = {"name": author.text}
        authors_names.append(author.text)
        if author.text not in authors_names_set:
            authors_names_set.add(author.text)
            authors_data.append(author_dict)
    return authors_names


def import_data(article_xml: str, dtd_file: str) -> None:
    """Given a XML entity, parses the required fields in order to store them to the database
    :param article_xml: The entity XML
    :param dtd_file: DTD file in order to parse correctly the XML
    :return: None
    """
    # Parse xml element
    dtd_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), dtd_file)
    dtd = f"<!DOCTYPE dblp SYSTEM '{dtd_path}'>"
    xml = dtd + article_xml
    parser = etree.XMLParser(load_dtd=True)
    tree = etree.fromstring(xml, parser=parser)

    authors = tree.xpath("//author")
    title = tree.xpath("//title")
    year = tree.xpath("//year")
    pages = tree.xpath("//pages")

    if not (authors and title and year and pages and title[0].text and year[0].text and pages[0].text):
        return

    title = title[0].text
    year = year[0].text
    pages = pages[0].text

    # Select papers between 2009 - 2015
    if not "2009" < year < "2015":
        return

    publication_dict = {"title": title, "year": year}

    if tree.tag == "article":
        journal = tree.xpath("//journal")
        if journal and journal[0].text:
            authors_names = extract_authors(authors)
            if f'{title + year}' not in article_titles_set:
                article_titles_set.add(f'{title + year}')
                article_data.append(publication_dict)

            if f'{journal[0].text}' not in journal_titles_set:
                journal_titles_set.add(f'{journal[0].text}')
                journal_data.append({'title': journal[0].text})

            article_journal_relations_data.append(((title, year), {}, journal[0].text))

            associate_authors_with_publications(authors_names, title, year, authors_article_relations_data,
                                                extract_pages_info(pages))

    elif tree.tag == "inproceedings":
        booktitle = tree.xpath("//booktitle")

        if booktitle and booktitle[0].text:
            authors_names = extract_authors(authors)
            if f'{title + year}' not in inproceedings_titles_set:
                inproceedings_titles_set.add(f'{title + year}')
                inproceedings_data.append(publication_dict)

            if booktitle[0].text not in conference_titles_set:
                conference_titles_set.add(booktitle[0].text)
                conference_data.append({'title': booktitle[0].text})

            inproceedings_conference_relations_data.append(
                ((title, year), {}, booktitle[0].text))

            associate_authors_with_publications(authors_names, title, year, authors_inproceedings_relations_data,
                                                extract_pages_info(pages))

    elif tree.tag == "incollection":
        booktitle = tree.xpath("//booktitle")
        publisher = tree.xpath("//publisher")

        if booktitle and booktitle[0].text:
            authors_names = extract_authors(authors)
            if f'{title + year}' not in incollection_titles_set:
                incollection_titles_set.add(f'{title + year}')
                if publisher and publisher[0].text:
                    publication_dict.update({'publisher': publisher[0].text})
                incollection_data.append(publication_dict)

            if booktitle[0].text not in book_titles_set:
                book_titles_set.add(booktitle[0].text)
                book_data.append({'title': booktitle[0].text})

            incollection_book_relations_data.append(((title, year), {}, booktitle[0].text))

            associate_authors_with_publications(authors_names, title, year, authors_incollection_relations_data,
                                                extract_pages_info(pages))


def parse_xml_gz_file(input_file: str, dtd_file: str) -> None:
    """Parses a given xml.gz file and extracts required data
    :param input_file: The xml.gz file
    :param dtd_file: DTD file in order to parse correctly the XML
    :return: None
    """
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
                    # print(count)
                    # count += 1
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
        # create_constraints()
        create_indices()
        parse_xml_gz_file(input_file=input_file, dtd_file=args.dtd[0])
        seed_database()
    else:
        print(f"File '{input_file}' cannot be processed, skipping.")

end = time.time()
print(f"Finished importing dataset, took {(end - start):.2f} seconds")
