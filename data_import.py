import gzip
import os
import time

from lxml import etree
from argparse import ArgumentParser

from app.db import db_connection


parser = ArgumentParser()
parser.add_argument('-f', nargs='+', help='The input file to parse')
parser.add_argument('-dtd', nargs='+', help='The DTD file')

args = parser.parse_args()
start = time.time()

open_tags = ['<article', '<inproceedings', '<incollection']
close_tags = ['</article>', '</inproceedings>', '</incollection>']


def import_data(article_xml: str, dtd_file: str) -> None:
    dtd_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), dtd_file)
    dtd = f'<!DOCTYPE dblp SYSTEM "{dtd_path}">'
    xml = dtd + article_xml
    parser = etree.XMLParser(load_dtd=True)
    tree = etree.fromstring(xml, parser=parser)
    print(etree.tostring(tree))


def parse_xml_gz_file(input_file: str, dtd_file: str) -> None:
    with gzip.open(input_file, 'rt') as f:
        extract = False
        buffer = ''
        for line in f:
            for tag in close_tags:
                if tag in line:
                    extract = False
                    idx = line.index(tag)
                    buffer += line[:idx] + tag
                    import_data(buffer, dtd_file)
                    # call parse here
                    buffer = ''
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
    if input_file.endswith('dblp.xml.gz'):
        parse_xml_gz_file(input_file=input_file, dtd_file=args.dtd[0])
    else:
        print(f"File '{input_file}' cannot be processed, skipping.")

end = time.time()
print(f"Finished importing dataset, took {(end - start):.2f} seconds")
