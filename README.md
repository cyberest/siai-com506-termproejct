# Estimating the impact of community activities to short squeeze in the financial market

## Proejct charter

### Problem statement

[r/wallstreetbets](https://www.reddit.com/r/wallstreetbets/) is a subreddit where participants discuss stock and options trading.
It is widely known that some subreddits, including this one, have influenced heavily the financial market.
In 2021, a phenomenal event happened - so-called the "short squeeze", which forced some hedge fund giants to step back from their short position.
Here, we try to analyze activities throughout this subreddit and use it, along with the other dataset comes from the traditional finance sector, to estimate the chance of short squeeze happening again.

### Goals & Objectives
The data collected from web scraping is relatively "unstructured", contrary to most of the data from the financial market.
The objective of this project is to construct a constant data pipeline, which performs ETL(Extract, Transform, Load) even without human intervention.
It is the general procedure of copying data from one or more sources into a destination system.

### Work scope
Reddit itself provides sophisticated data API and there are also lots of third-party data providers.
In this regard, scraping Reddit website is the smartest way of collecting data in demand.
Therefore, instead of constructing an advanced web scraping system, we focus on understanding the underlying structure of the Reddit website, which can be extended to the identification of the correct DGP(Data Generating Process) for future analysis.

To be specific:
- The scraping target is limited to just one subreddit - wallstreetbets.
- Unfortunately, we have found out that Reddit does not provide any information beyond the most recent 500 posts. 
- Moreover, Reddit is most likely to monitor unauthorized web scraping which might impact website performance or cost.
- Considering these restrictions, the work scope of the project is limited to providing a practitioner guideline of the procedure, rather than a complete model.
- Nevertheless, with the code presented, we can keep gathering the most recent threads from the board.
- And stored these, including not only text but also images files, in SQL/NoSQL databases (SQLite and Elasticsearch respectively).

### Timeline
Its inefficiency and restrictions mentioned above, this project is most likely a one-off task.
However, the most simple form of automation is implemeted with cron and bash script.
Under the current settings, the main scraping script will run every day at the specified time.
Given any monitoring and logging procedure is not provided, the script should be used with care.

### Responsibilities
This project is solely conducted by myself and was a part of an educational assignment.
All responsibilities should be directed to me.
If you would like to get in touch, please contact ```cyberest@gmail.com```.


## How to install
These instructions will get you a copy of the project up and running on your local machine (or cloud environment, upon your choice)

### Clone
Clone this repo to your local machine
```
git clone https://github.com/cyberest/COM506.git
```

### Setup
Build a docker image using the DockerFile

```
docker build --tag <your_choice> ./docker/Dockerfile
```
you can find the newly created
```
docker images
```


Start a group of related docker containers
```
docker-compose up -d
```

upon modification, rebuild with the command
```
docker build --tag [태그명] .
```

## How to Run
1. To set the configurations, use ```config.ini```.

2. To initiate a scraping batch, use the command below.
```
python main.py -export_opt=<export_option> -clean=<true or false (optional)>
```
Possible options for ```<export_option>``` are:
- csv: download as CSV file at ```/output```
- sql: upload to Sqlite
- nosql: upload to Elasticsearch
- all: csv, sql and nosql

3. To visualize data, Kibana is provided as a part of docker-compose. However, nothing is implemented yet.


## Contributors
[JunYoung Park](https://github.com/cyberest)

## Project Organization
    ├── data
    │   ├── elasticsearch                <- NoSQL database.
    │   ├── images                       <- Downloaded images renamed by its MD5 hash for future reference.
    │   └── sqlite                       <- Simple SQL database.
    ├── docker
    │   ├── Dockerfile                   <- DockerFile to build main (Jupyter-python) image.
    │   └── requirement.txt              <- The requirements file for reproducing or updating the environment.
    ├── notebook
    │   ├── ER-diagram.ipynb             <- E-R diagram for SQL database.
    │   ├── Development.ipynb            <- Jupyter notebook with trial&error during development.
    │   └── NoSQLmap.json                <- NoSQL schema defined.
    ├── RedditScraper                    
    │   ├── __init__.py                   
    │   ├── config_parser.py             <- Script to parse configurations into dict.
    │   ├── data_manager.py              <- Class for data-related operations.
    │   ├── helper_functions.py          <- Custom helper functions for web crawling
    │   └── web_scraper                  <- Powerhorse of the project.
    ├── .gitignore                       <- Files that should be ignored.
    ├── config.ini                       <- Configurations.
    ├── docker-compose.yml               <- Automated orchestration for a group of docker containers.
    ├── main.py                          <- Main code.
    ├── README.md                        <- RTFM(Read The Full Manuel)
    └── scheduled_run.sh                 <- Automated script for daily run
