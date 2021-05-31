# DBLP Neo4J FastAPI

[![Python](https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9-blue.svg?logo=python&logoColor=white)](https://www.python.org/)  [![Neo4J](https://img.shields.io/badge/Neo4j-4.2.x-589636.svg?logo=neo4j&logoColor=white)](https://neo4j.com/) [![Neo4J](https://img.shields.io/badge/FastAPI-0.65.x-589636.svg?logo=fastapi&logoColor=white)](https://neo4j.com/)

This repository contains a FastAPI application that connects to a Neo4j Database and process some metrics for DBLP computer science bibliography.

All the data used for the development can be found [here](https://dblp.uni-trier.de/xml/).


## FastAPI Application

### Installation from source

This section contains the installation instructions in order to set up a local development environment. The instructions
have been validated for Ubuntu 20.04.

First, install all required software:

Python 3.7+

```bash
sudo apt update
sudo apt install git python3 python3-pip python3-dev
```

The project dependencies are managed with [pipenv](https://docs.pipenv.org/en/latest/). You can install it with:

```bash
pip install --user pipenv
```

`pipenv` should now be in your `PATH`. If not, logout and log in again. Then install all dependencies with:

```bash
pipenv install --dev
```

Then you can enable the python environment with:

```bash
pipenv shell
```

All commands from this point forward require the python environment to be enabled.

### Environment variables

The project uses environment variables in order to keep private data like user names and passwords out of source
control. You can either set them at system level, or by creating a file named `.env` at the root of the repository. 
The required environment variables for development are:

* `DB_PASSWORD`: The database user password 
* `DB_HOST`: The database host. _For local development use_ `localhost`

### Local Development

In order to run the project on your workstation, I recommend using the docker file to install Neo4J. (Instructions are listed below)

To populate the database run the following command:

```bash
python data_import.py -f <xml.gz file> -dtd <dtd file>
```

_Example_
```bash
python data_import.py -f assist_material/dblp.xml.gz -dtd assist_material/dblp.dtd
```

The importing procedure stores approximately 500K nodes and 800K relationships with records of years: 2009-2015. Generally, 
the supported xml from the DBLP site contains millions of entries but due to lack of computing power I decided to limit a bit 
the imported entries.

Now you can run the web server with:

```bash
uvicorn app.main:app
```

The API is available at `http://127.0.0.1:8000/api/v1/`

The documentation Swagger page of the API is available at `http://127.0.0.1:8000/docs` or with ReDoc `http://127.0.0.1:8000/redoc`


## Installation using Docker

I recommend this way of installation in order to keep your machine clean from packages that you may not use ever again. 
 
Initially, install [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) (click the link to see
 instructions) & [Docker Compose](https://docs.docker.com/compose/install/) in order to build the project.
 
__Set up the `.env` at the root of the repository!__
* `DB_PASSWORD`: The database user password 
* `DB_HOST`: `neo4j` _The host name __must__ be `neo4j`_ 

Then just execute the following:

```bash
docker-compose up --build
```

Then you have the database & the API up and running!

If you want to expose only the database as docker instance run the following:

```bash
docker-compose up neo4j
```

In order to perform the import of the data you can log in to the running docker container and perform the process
 manually.

```bash
docker exec -it api bash
```

Now you have access to all the files of the API. __You can now run the import command as mentioned above in the Local
Development section.__

The database is exposed at `localhost:7474`

The API & the documentation pages page are available to the same addresses that referred above.


## Endpoints

The endpoints implementation along with the Cypher Queries can be found [here](link).

For the results below is used my development machine (i7-2600, 16GB RAM, 120GB SSD) with 530K nodes 847K relationships 
stored on the database.

### GET /api/v1/query-1

Find the titles (title, year) of publications that a particular author has published.

__params__  
author: string  

eg.

```text
curl http://0.0.0.0:8000/api/v1/query-1?author=Bir%20Bhanu

[
  {
    "title": "Evolving Bayesian Graph for Three-Dimensional Vehicle Model Building From Video.",
    "year": 2014
  },
  {
    "title": "Automated detection of brain abnormalities in neonatal hypoxia ischemic injury from MR images.",
    "year": 2014
  },
  {
    "title": "Bio-Driven Cell Region Detection in Human Embryonic Stem Cell Assay.",
    "year": 2014
  },
  {
    "title": "Predictive models for multibiometric systems.",
    "year": 2014
  },
  {
    "title": "Face image super-resolution using 2D CCA.",
    "year": 2014
  },
  {
    "title": "Visual and Contextual Modeling for the Detection of Repeated Mild Traumatic Brain Injury.",
    "year": 2014
  },
  {
    "title": "Structural Signatures for Passenger Vehicle Classification in Video.",
    "year": 2013
  },
  {
    "title": "Reference-Based Scheme Combined With K-SVD for Scene Image Categorization.",
    "year": 2013
  },
  {
    "title": "Learning small gallery size for prediction of recognition performance on large populations.",
    "year": 2013
  },
  {
    "title": "Dynamic Bayesian Networks for Vehicle Classification in Video.",
    "year": 2012
  },
  {
    "title": "Ear Shape for Biometric Identification.",
    "year": 2011
  },
  {
    "title": "Incremental Unsupervised Three-Dimensional Vehicle Model Learning From Video.",
    "year": 2010
  }
]

response time 24.2 ms

```

### GET /api/v1/query-2

Find the co-authors of an author (name, number of co-authorships) for a particular year.

__params__  
author: string   
year:   string   

eg.

```text
curl http://0.0.0.0:8000/api/v1/query-2?author=Bir%20Bhanu&year=2013
[
  {
    "name": "Ninad Thakoor",
    "count": 2
  },
  {
    "name": "Le An",
    "count": 1
  },
  {
    "name": "Honggang Zhang 0002",
    "count": 1
  },
  {
    "name": "Jun Guo 0002",
    "count": 1
  },
  {
    "name": "Qun Li",
    "count": 1
  },
  {
    "name": "Rong Wang",
    "count": 1
  }
]

response time 14.9 ms
```

### GET /api/v1/query-3

Find the top-K authors (name, count) with regard to most conference/journal publications.

__params__   
limit:  int
inproc: boolean

eg.  
```text
curl http://0.0.0.0:8000/api/v1/query-3?limit=10&inproc=true

[
  {
    "name": "Maciej Paszynski",
    "count": 13
  },
  {
    "name": "Yong Shi 0001",
    "count": 12
  },
  {
    "name": "Cihan H. Dagli",
    "count": 11
  },
  {
    "name": "David Pardo",
    "count": 11
  },
  {
    "name": "Farideh Hamidi",
    "count": 11
  },
  {
    "name": "Emilio Luque",
    "count": 11
  },
  {
    "name": "Adem Karahoca",
    "count": 11
  },
  {
    "name": "John Shawe-Taylor",
    "count": 10
  },
  {
    "name": "Slawomir Koziel",
    "count": 10
  },
  {
    "name": "Yoshua Bengio",
    "count": 10
  }
]

response time 33.7 ms
```

```text
curl http://0.0.0.0:8000/api/v1/query-3?limit=10&inproc=false

[
  {
    "name": "Peng Shi 0001",
    "count": 119
  },
  {
    "name": "Lajos Hanzo",
    "count": 97
  },
  {
    "name": "Chin-Chen Chang 0001",
    "count": 96
  },
  {
    "name": "Stevo Stevic",
    "count": 87
  },
  {
    "name": "Mohamed-Slim Alouini",
    "count": 84
  },
  {
    "name": "Licheng Jiao",
    "count": 78
  },
  {
    "name": "Paul M. Thompson",
    "count": 75
  },
  {
    "name": "Jürgen Bajorath",
    "count": 71
  },
  {
    "name": "Zheng Bao",
    "count": 70
  },
  {
    "name": "Witold Pedrycz",
    "count": 67
  }
]

response time 1.44 s
```

### GET /api/v1/query-4

Find the top-K authors (name, count) with regard to most co-authors in a single work.

__params__  
limit: int  

eg.  

```text
curl http://0.0.0.0:8000/api/v1/query-4?limit=10

[
  {
    "name": "Toshiaki Katayama",
    "count": 141
  },
  {
    "name": "Juan Carlos Augusto",
    "count": 96
  },
  {
    "name": "Peter V. Kochunov",
    "count": 90
  },
  {
    "name": "Sujeet Shenoi",
    "count": 90
  },
  {
    "name": "Yong Li 0008",
    "count": 89
  },
  {
    "name": "Clifford W. Hansen",
    "count": 89
  },
  {
    "name": "Bob Coecke",
    "count": 88
  },
  {
    "name": "Oswin Aichholzer",
    "count": 85
  },
  {
    "name": "Alberto H. F. Laender",
    "count": 83
  },
  {
    "name": "Jack J. Dongarra",
    "count": 80
  }
]

response time 5.29 s
```

### GET /api/v1/query-5

Find the top-K authors (name, count) with regard to most co-authors in a particular year.

__params__  
year:   string  
limit:  int

eg.  

```text
curl http://0.0.0.0:8000/api/v1/query-5?limit=10&year=2013

[
  {
    "name": "Arthur W. Toga",
    "count": 159
  },
  {
    "name": "Matthew F. Glasser",
    "count": 130
  },
  {
    "name": "David C. Van Essen",
    "count": 129
  },
  {
    "name": "Paul M. Thompson",
    "count": 126
  },
  {
    "name": "Abraham Z. Snyder",
    "count": 115
  },
  {
    "name": "Kamil Ugurbil",
    "count": 99
  },
  {
    "name": "Neda Jahanshad",
    "count": 96
  },
  {
    "name": "Jesper L. R. Andersson",
    "count": 92
  },
  {
    "name": "Junqian Xu",
    "count": 91
  },
  {
    "name": "Eugene Kolker",
    "count": 89
  }
]

response time 3.93 s
```

### GET /api/v1/query-6

Find the top-K authors (name, count) with regard to most active years.

__params__  
limit: int  
 
eg.  

```text
curl http://0.0.0.0:8000/api/v1/query-6?limit=10

[
  {
    "name": "Radu Sion",
    "count": 5
  },
  {
    "name": "Arun Ross",
    "count": 5
  },
  {
    "name": "Cristina Nita-Rotaru",
    "count": 5
  },
  {
    "name": "Stan Z. Li",
    "count": 5
  },
  {
    "name": "Wenjing Lou",
    "count": 5
  },
  {
    "name": "Pierangela Samarati",
    "count": 5
  },
  {
    "name": "Kui Ren 0001",
    "count": 5
  },
  {
    "name": "Lars R. Knudsen",
    "count": 5
  },
  {
    "name": "Bir Bhanu",
    "count": 5
  },
  {
    "name": "Kar-Ann Toh",
    "count": 5
  }
]

response time 3.26 s
```

### GET /api/v1/query-7  

Find the top-K authors (name, count) with regard to most co-authors that have not published together.

__params__   
limit: int  

eg.  

```text
curl http://0.0.0.0:8000/api/v1/query-7?limit=10

[
  {
    "name": "Arthur W. Toga",
    "count": 95626
  },
  {
    "name": "Paul M. Thompson",
    "count": 78180
  },
  {
    "name": "Sébastien Ourselin",
    "count": 36320
  },
  {
    "name": "Yu Zhang",
    "count": 36073
  },
  {
    "name": "Vince D. Calhoun",
    "count": 31625
  },
  {
    "name": "Athanasios V. Vasilakos",
    "count": 27465
  },
  {
    "name": "Mark Jenkinson",
    "count": 25229
  },
  {
    "name": "Bram van Ginneken",
    "count": 24820
  },
  {
    "name": "Bruce Fischl",
    "count": 23922
  },
  {
    "name": "Nassir Navab",
    "count": 23829
  }
]

response time 4.98 m
```

Really expensive query...


### GET /api/v1/query-8 

Find the top-K authors (name, count) with regard to largest average number of journal publications per year 
(consider only active years).

__params__   
limit: int  

eg.  

```text
curl http://0.0.0.0:8000/api/v1/query-8?limit=10

[
  {
    "name": "Burt Kaliski",
    "count": 38
  },
  {
    "name": "Gerrit Bleumer",
    "count": 34
  },
  {
    "name": "Peng Shi 0001",
    "count": 23
  },
  {
    "name": "Friedrich L. Bauer",
    "count": 20
  },
  {
    "name": "Lajos Hanzo",
    "count": 19
  },
  {
    "name": "Chin-Chen Chang 0001",
    "count": 19
  },
  {
    "name": "Stevo Stevic",
    "count": 17
  },
  {
    "name": "Carlisle Adams",
    "count": 17
  },
  {
    "name": "Mohamed-Slim Alouini",
    "count": 16
  },
  {
    "name": "Licheng Jiao",
    "count": 15
  }
]

response time 2.59 s
```

### GET /api/v1/query-9 

Find the top-K authors (name, count) that a given author has not worked with, with regard to most 
co-authorships with authors that the given author has worked with.

__params__   
limit: int  

eg.  

```text
curl http://0.0.0.0:8000/api/v1/query-9?limit=10

[
  {
    "name": "Athanasios V. Vasilakos",
    "count": 2223
  },
  {
    "name": "Arthur W. Toga",
    "count": 2188
  },
  {
    "name": "Mark Jenkinson",
    "count": 2005
  },
  {
    "name": "Paul M. Thompson",
    "count": 1978
  },
  {
    "name": "Stephen M. Smith",
    "count": 1916
  },
  {
    "name": "Alan C. Evans",
    "count": 1845
  },
  {
    "name": "D. Louis Collins",
    "count": 1759
  },
  {
    "name": "Laurence T. Yang",
    "count": 1724
  },
  {
    "name": "Sébastien Ourselin",
    "count": 1722
  },
  {
    "name": "Jing Li",
    "count": 1684
  }
]

response time 35 m
```

The slowest query of all.


### GET /api/v1/query-10

Find the authors (name, count) that have published more than three works in a given single year.

__params__   
limit: int
year:  string

eg.  

```text
curl http://0.0.0.0:8000/api/v1/query-10?limit=10&year=2011

[
  {
    "name": "Burt Kaliski",
    "count": 38
  },
  {
    "name": "Gerrit Bleumer",
    "count": 34
  },
  {
    "name": "Alex Biryukov",
    "count": 32
  },
  {
    "name": "Lajos Hanzo",
    "count": 29
  },
  {
    "name": "Bart Preneel",
    "count": 25
  },
  {
    "name": "Peng Shi 0001",
    "count": 24
  },
  {
    "name": "Friedrich L. Bauer",
    "count": 20
  },
  {
    "name": "Jürgen Bajorath",
    "count": 18
  },
  {
    "name": "Marijke De Soete",
    "count": 18
  },
  {
    "name": "Sabrina De Capitani di Vimercati",
    "count": 17
  }
]

response time 859 ms
```

###  GET /api/v1/query-11

Find the number of pages that a particular author has published in a given year.

__params__  
author: string   
year:   string  
 
eg.  

```text
curl http://0.0.0.0:8000/api/v1/query-11?author=Bir%20Bhanu&year=2014

[
  {
    "total_pages": 66
  }
]

response time 11.3 ms
```

###  GET /api/v1/query-12

Find the top-K authors (name, count) with regard to articles published in a particular journal as a first/last author 
in a given year.

__params__  
title:        string   
year:         string
limit:        int
first_author: boolean
 
eg.  

```text
curl http://0.0.0.0:8000/api/v1/query-12?title=Reliab.%20Comput.&year=2013&limit=10&first_author=true

[
  {
    "name": "Andreas Rauh",
    "count": 3
  },
  {
    "name": "Raazesh Sainudiin",
    "count": 2
  },
  {
    "name": "Stefan Kiel",
    "count": 1
  },
  {
    "name": "Shinya Miyajima",
    "count": 1
  },
  {
    "name": "Olivier Mullier",
    "count": 1
  },
  {
    "name": "Hao Jiang 0001",
    "count": 1
  },
  {
    "name": "Maryam Shams Solary",
    "count": 1
  },
  {
    "name": "Dmitry Yu. Nadezhin",
    "count": 1
  },
  {
    "name": "Anatoly V. Panyukov",
    "count": 1
  },
  {
    "name": "Alexander V. Prolubnikov",
    "count": 1
  }
]

response time 13.3 ms
```

```text
http://0.0.0.0:8000/api/v1/query-12?title=Reliab.%20Comput.&year=2013&limit=10&first_author=false

[
  {
    "name": "Ekaterina Auer",
    "count": 2
  },
  {
    "name": "Vladik Kreinovich",
    "count": 2
  },
  {
    "name": "Sylvie Putot",
    "count": 1
  },
  {
    "name": "Sergei I. Zhilin",
    "count": 1
  },
  {
    "name": "Valentin A. Golodov",
    "count": 1
  },
  {
    "name": "Philippe Théveny",
    "count": 1
  },
  {
    "name": "Irina V. Surodina",
    "count": 1
  },
  {
    "name": "Xiangke Liao",
    "count": 1
  },
  {
    "name": "Elena V. Chausova",
    "count": 1
  },
  {
    "name": "Andreas Rauh",
    "count": 1
  }
]

response time 53.3 ms
```

###  GET /api/v1/query-13

Find the three authors that have appeared as co-authors for the most times in a particular journal.

__params__  
title:  string   
limit:  int
 
eg.  

```text
curl http://0.0.0.0:8000/api/v1/query-13?title=Reliab.%20Comput.&limit=10

[
  {
    "name1": "Ekaterina Auer",
    "name2": "Andreas Rauh",
    "name3": "Harald Aschemann",
    "count": 3
  },
  {
    "name1": "Andreas Rauh",
    "name2": "Harald Aschemann",
    "name3": "Eberhard P. Hofer",
    "count": 2
  },
  {
    "name1": "Tanja Magoc",
    "name2": "Martine Ceberio",
    "name3": "François Modave",
    "count": 2
  },
  {
    "name1": "Erik-Jan van Kampen",
    "name2": "Qiping Chu",
    "name3": "J. A. Mulder",
    "count": 2
  },
  {
    "name1": "Andreas Rauh",
    "name2": "Harald Aschemann",
    "name3": "Luise Senkel",
    "count": 2
  },
  {
    "name1": "Hao Jiang 0001",
    "name2": "Lizhi Cheng",
    "name3": "Roberto Barrio",
    "count": 1
  },
  {
    "name1": "Hao Jiang 0001",
    "name2": "Lizhi Cheng",
    "name3": "Xiangke Liao",
    "count": 1
  },
  {
    "name1": "Olivier Mullier",
    "name2": "Eric Goubault",
    "name3": "Michel Kieffer",
    "count": 1
  },
  {
    "name1": "Housen Li",
    "name2": "Lizhi Cheng",
    "name3": "Roberto Barrio",
    "count": 1
  },
  {
    "name1": "Eric Goubault",
    "name2": "Michel Kieffer",
    "name3": "Sylvie Putot",
    "count": 1
  }
]

response time 1.03 s
```

###  GET /api/v1/query-14

Find pairs of authors that have appeared in different parts of the same book and have never co-authored a work.

__params__  
limit:  int
 
eg.  

```text
http://0.0.0.0:8000/api/v1/query-14?limit=10

[
  {
    "name1": "Bir Bhanu",
    "name2": "Marijke De Soete"
  },
  {
    "name1": "Marijke De Soete",
    "name2": "Xiaokui Xiao"
  },
  {
    "name1": "Dan Boneh",
    "name2": "Xiaokui Xiao"
  },
  {
    "name1": "Friedrich L. Bauer",
    "name2": "Xiaokui Xiao"
  },
  {
    "name1": "Robert J. Zuccherato",
    "name2": "Xiaokui Xiao"
  },
  {
    "name1": "Gerrit Bleumer",
    "name2": "Xiaokui Xiao"
  },
  {
    "name1": "Nicolas Thériault",
    "name2": "Xiaokui Xiao"
  },
  {
    "name1": "Roberto Avanzi",
    "name2": "Xiaokui Xiao"
  },
  {
    "name1": "Bart Preneel",
    "name2": "Xiaokui Xiao"
  },
  {
    "name1": "Marc Vauclair",
    "name2": "Xiaokui Xiao"
  }
]

response time 210 ms
```

###  GET /api/v1/query-15

Find the authors that have published work for K consecutive years.

__params__ 
k:      int
limit:  int
 
eg.  

```text
http://0.0.0.0:8000/api/v1/query-15?limit=10&k=3

[
  {
    "name": "Sean W. Smith",
    "consecutiveYears": 3
  },
  {
    "name": "Adi Shamir",
    "consecutiveYears": 3
  },
  {
    "name": "Bart Preneel",
    "consecutiveYears": 3
  },
  {
    "name": "Yvo Desmedt",
    "consecutiveYears": 3
  },
  {
    "name": "Sabrina De Capitani di Vimercati",
    "consecutiveYears": 3
  },
  {
    "name": "Salil P. Vadhan",
    "consecutiveYears": 3
  },
  {
    "name": "Tor Helleseth",
    "consecutiveYears": 3
  },
  {
    "name": "Tim Güneysu",
    "consecutiveYears": 3
  },
  {
    "name": "Paulo S. L. M. Barreto",
    "consecutiveYears": 3
  },
  {
    "name": "Wensheng Zhang",
    "consecutiveYears": 3
  }
]

response time 4.33 s
```

###  GET /api/v1/query-16

Find the top-K authors with regard to average number of co-authors in their publications.

__params__ 
limit:  int
 
eg.  

```text
http://0.0.0.0:8000/api/v1/query-16?limit=10

[
  {
    "name": "Pattie Maes",
    "averageCoAuthors": 100.0
  },
  {
    "name": "Doron Lancet",
    "averageCoAuthors": 58.0
  },
  {
    "name": "Takeshi Kawashima",
    "averageCoAuthors": 50.0
  },
  {
    "name": "Mitsuteru Nakao",
    "averageCoAuthors": 47.5
  },
  {
    "name": "Itiro Siio",
    "averageCoAuthors": 47.0
  },
  {
    "name": "Alexandre Alapetite",
    "averageCoAuthors": 46.0
  },
  {
    "name": "Roel Vertegaal",
    "averageCoAuthors": 44.0
  },
  {
    "name": "Peter Selinger",
    "averageCoAuthors": 44.0
  },
  {
    "name": "Henry Holtzman",
    "averageCoAuthors": 44.0
  },
  {
    "name": "Dmitrij Frishman",
    "averageCoAuthors": 43.0
  }
]

response time 28.9 s
```

###  GET /api/v1/query-17

Find the authors of consecutively published papers with more than a given amount of years between them.

__params__ 
limit:  int
 
eg.  

```text
http://0.0.0.0:8000/api/v1/query-17?limit=10

[
  {
    "name": "Yu-Ru Lin",
    "yearsDifferences": [
      1,
      1,
      2
    ]
  },
  {
    "name": "Claudio Bettini",
    "yearsDifferences": [
      1,
      1,
      2
    ]
  },
  {
    "name": "Sudeep Sarkar",
    "yearsDifferences": [
      1,
      1,
      2
    ]
  },
  {
    "name": "Jesse Hoey",
    "yearsDifferences": [
      1,
      1,
      2
    ]
  },
  {
    "name": "Sean W. Smith",
    "yearsDifferences": [
      1,
      1,
      2
    ]
  },
  {
    "name": "Bart Preneel",
    "yearsDifferences": [
      1,
      1,
      2
    ]
  },
  {
    "name": "Kaoru Kurosawa",
    "yearsDifferences": [
      1,
      1,
      2
    ]
  },
  {
    "name": "Jaideep Vaidya",
    "yearsDifferences": [
      1,
      1,
      2
    ]
  },
  {
    "name": "Adi Shamir",
    "yearsDifferences": [
      1,
      1,
      2
    ]
  },
  {
    "name": "Thomas Franz",
    "yearsDifferences": [
      1,
      1,
      2
    ]
  }
]

response time 3.2 s
```

###  GET /api/v1/query-18

Find the author (name, count) with the most parts in a single book of collective works.

eg.  

```text
http://0.0.0.0:8000/api/v1/query-18

[
  {
    "name": "Burt Kaliski",
    "title": "Encyclopedia of Cryptography and Security (2nd Ed.)",
    "parts": 38
  }
]

response time 78.2 s
```


## Database Schema  

A higher level visualization of the schema is the following:

![schema](link)

Also, by running `CALL apoc.meta.schema() YIELD value UNWIND keys(value) AS key RETURN key, value[key] AS value;` we can 
extract the detailed schema of the database.

```json
[
  {
    "key": "Incollection",
    "value": {
"count": 3801,
"relationships": {
"CONTRIBUTED": {
"count": 10422,
"properties": {
"total_pages": {
"existence": false,
"type": "INTEGER",
"array": false
            },
"end_page": {
"existence": false,
"type": "INTEGER",
"array": false
            },
"start_page": {
"existence": false,
"type": "INTEGER",
"array": false
            },
"first_author": {
"existence": false,
"type": "BOOLEAN",
"array": false
            },
"last_author": {
"existence": false,
"type": "BOOLEAN",
"array": false
            }
          },
"direction": "in",
"labels": [
            "Author"
          ]
        },
"PUBLISHED": {
"count": 461725,
"properties": {

          },
"direction": "out",
"labels": [
            "Book"
          ]
        }
      },
"type": "node",
"properties": {
"title": {
"existence": false,
"type": "STRING",
"indexed": true,
"unique": false
        },
"year": {
"existence": false,
"type": "STRING",
"indexed": true,
"unique": false
        }
      },
"labels": []
    }
  },
  {
    "key": "PUBLISHED",
    "value": {
"count": 206123,
"type": "relationship",
"properties": {

      }
    }
  },
  {
    "key": "Book",
    "value": {
"count": 32,
"relationships": {
"PUBLISHED": {
"count": 1270,
"properties": {

          },
"direction": "in",
"labels": [
            "Incollection"
          ]
        }
      },
"type": "node",
"properties": {
"title": {
"existence": false,
"type": "STRING",
"indexed": true,
"unique": false
        }
      },
"labels": []
    }
  },
  {
    "key": "Article",
    "value": {
"count": 197718,
"relationships": {
"CONTRIBUTED": {
"count": 10422,
"properties": {
"total_pages": {
"existence": false,
"type": "INTEGER",
"array": false
            },
"end_page": {
"existence": false,
"type": "INTEGER",
"array": false
            },
"start_page": {
"existence": false,
"type": "INTEGER",
"array": false
            },
"first_author": {
"existence": false,
"type": "BOOLEAN",
"array": false
            },
"last_author": {
"existence": false,
"type": "BOOLEAN",
"array": false
            }
          },
"direction": "in",
"labels": [
            "Author"
          ]
        },
"PUBLISHED": {
"count": 1377523,
"properties": {

          },
"direction": "out",
"labels": [
            "Journal"
          ]
        }
      },
"type": "node",
"properties": {
"title": {
"existence": false,
"type": "STRING",
"indexed": true,
"unique": false
        },
"year": {
"existence": false,
"type": "STRING",
"indexed": true,
"unique": false
        }
      },
"labels": []
    }
  },
  {
    "key": "Author",
    "value": {
"count": 325266,
"relationships": {
"CONTRIBUTED": {
"count": 9237,
"properties": {
"total_pages": {
"existence": false,
"type": "INTEGER",
"array": false
            },
"end_page": {
"existence": false,
"type": "INTEGER",
"array": false
            },
"start_page": {
"existence": false,
"type": "INTEGER",
"array": false
            },
"first_author": {
"existence": false,
"type": "BOOLEAN",
"array": false
            },
"last_author": {
"existence": false,
"type": "BOOLEAN",
"array": false
            }
          },
"direction": "out",
"labels": [
            "Article",
            "Incollection",
            "Inproceedings"
          ]
        }
      },
"type": "node",
"properties": {
"name": {
"existence": false,
"type": "STRING",
"indexed": true,
"unique": false
        }
      },
"labels": []
    }
  },
  {
    "key": "Journal",
    "value": {
"count": 659,
"relationships": {
"PUBLISHED": {
"count": 1068,
"properties": {

          },
"direction": "in",
"labels": [
            "Article"
          ]
        }
      },
"type": "node",
"properties": {
"title": {
"existence": false,
"type": "STRING",
"indexed": true,
"unique": false
        }
      },
"labels": []
    }
  },
  {
    "key": "Inproceedings",
    "value": {
"count": 2910,
"relationships": {
"CONTRIBUTED": {
"count": 10422,
"properties": {
"total_pages": {
"existence": false,
"type": "INTEGER",
"array": false
            },
"end_page": {
"existence": false,
"type": "INTEGER",
"array": false
            },
"start_page": {
"existence": false,
"type": "INTEGER",
"array": false
            },
"first_author": {
"existence": false,
"type": "BOOLEAN",
"array": false
            },
"last_author": {
"existence": false,
"type": "BOOLEAN",
"array": false
            }
          },
"direction": "in",
"labels": [
            "Author"
          ]
        },
"PUBLISHED": {
"count": 1036165,
"properties": {

          },
"direction": "out",
"labels": [
            "Conference"
          ]
        }
      },
"type": "node",
"properties": {
"title": {
"existence": false,
"type": "STRING",
"indexed": true,
"unique": false
        },
"year": {
"existence": false,
"type": "STRING",
"indexed": true,
"unique": false
        }
      },
"labels": []
    }
  },
  {
    "key": "CONTRIBUTED",
    "value": {
"count": 640763,
"type": "relationship",
"properties": {
"total_pages": {
"existence": false,
"type": "INTEGER",
"array": false
        },
"end_page": {
"existence": false,
"type": "INTEGER",
"array": false
        },
"start_page": {
"existence": false,
"type": "INTEGER",
"array": false
        },
"first_author": {
"existence": false,
"type": "BOOLEAN",
"array": false
        },
"last_author": {
"existence": false,
"type": "BOOLEAN",
"array": false
        }
      }
    }
  },
  {
    "key": "Conference",
    "value": {
"count": 31,
"relationships": {
"PUBLISHED": {
"count": 3117,
"properties": {

          },
"direction": "in",
"labels": [
            "Inproceedings"
          ]
        }
      },
"type": "node",
"properties": {
"title": {
"existence": false,
"type": "STRING",
"indexed": true,
"unique": false
        }
      },
"labels": []
    }
  }
]
```

__Indexes__

```python
graph_db.run("CREATE INDEX AuthorNameIndex IF NOT EXISTS FOR (t:Author) ON (t.name)")
graph_db.run("CREATE INDEX ArticleTitleYearIndex IF NOT EXISTS FOR (t:Article) ON (t.title, t.year)")
graph_db.run("CREATE INDEX InproceedingsTitleYearIndex IF NOT EXISTS FOR (t:Inproceedings) ON (t.title, t.year)")
graph_db.run("CREATE INDEX IncollectionTitleYearIndex IF NOT EXISTS FOR (t:Incollection) ON (t.title, t.year)")
graph_db.run("CREATE INDEX ArticleTitleIndex IF NOT EXISTS FOR (t:Article) ON (t.title)")
graph_db.run("CREATE INDEX InproceedingsTitleIndex IF NOT EXISTS FOR (t:Inproceedings) ON (t.title)")
graph_db.run("CREATE INDEX IncollectionTitleIndex IF NOT EXISTS FOR (t:Incollection) ON (t.title)")
graph_db.run("CREATE INDEX ArticleYearIndex IF NOT EXISTS FOR (t:Article) ON (t.year)")
graph_db.run("CREATE INDEX InproceedingsYearIndex IF NOT EXISTS FOR (t:Inproceedings) ON (t.year)")
graph_db.run("CREATE INDEX IncollectionYearIndex IF NOT EXISTS FOR (t:Incollection) ON (t.year)")
graph_db.run("CREATE INDEX JournalTitleIndex IF NOT EXISTS FOR (t:Journal) ON (t.title)")
graph_db.run("CREATE INDEX ConferenceIndex IF NOT EXISTS FOR (t:Conference) ON (t.title)")
graph_db.run("CREATE INDEX BookTitleIndex IF NOT EXISTS FOR (t:Book) ON (t.title)")
```
