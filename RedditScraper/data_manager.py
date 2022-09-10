# Data manager
# ===================

import time
import os
import shutil

import csv
import json
import pandas as pd

import sqlite3
from elasticsearch import Elasticsearch, helpers

from .web_scraper import RedditScraper


"""Inherited RedditScraper and added Database operations"""
class RedditDataManager(RedditScraper):

    def __init__(self, subreddit, output_dir, image_dir, data_dir, elastic_server, nosql_mapping):
        self.subreddit = subreddit
        self.OUTPUT_DIR = output_dir
        self.IMAGE_DIR = image_dir
        self.DATA_DIR = data_dir
        self.ELASTIC_SERVER = elastic_server
        self.NOSQL_MAPPING = nosql_mapping

    # Cleanup output data
    def cleanup_output(self):
        # Remove images downloaded
        shutil.rmtree(self.OUTPUT_DIR)
        os.makedirs(self.OUTPUT_DIR)

    # Download collected records in CSV format
    def download_csv(self):
        columns_headers = list(self.threads[0].keys())
        file_name = f'{self.subreddit}_{int(time.time())}.csv'

        with open(self.OUTPUT_DIR + file_name, 'a', encoding='utf-8') as f:
            # used tab delimiter - content contains many commas
            writer = csv.DictWriter(f, quoting=csv.QUOTE_ALL, fieldnames=columns_headers)
            writer.writerow(dict((fn,fn) for fn in columns_headers))
            for thread in self.threads:
                writer.writerow(thread)
        print(f'CSV export completeted: {file_name}')

    # Converts collected records to Pandas DataFrame
    def threads_to_df(self):
        if self.threads:
            df = pd.DataFrame(self.threads)

            # Datatype adjustments for DB upload
            # df['time'] = pd.to_datetime(df['time']) # object to datetime64, not compatible for sqlite
            df.loc[df['author_awards'].apply(len).eq(0), 'author_awards'] = None # replace {} with None
            df['author_awards'] = df['author_awards'].apply(json.dumps) # Serialize dict with JSON
            df.loc[df['media'].apply(len).eq(0), 'media'] = None # replace [] with None
            df['media'] = df['media'].apply(json.dumps) # Serialize list with JSON

            self.threads_df = df
            return df
    
    # Establish connection to NoSQL server
    def sql_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.DATA_DIR + f"sqlite/reddit_scrap.db")
        except Exception as e:
            print("Failed to establish SQL connection: ", e)
        return conn

    # Upload collected records into SQL database
    def upload_sql(self):
        conn = self.sql_connection()
        try:
            cur = conn.cursor()
            conn.execute(f"""CREATE TABLE IF NOT EXISTS reddit_thread_{self.subreddit}(
                post_id TEXT PRIMARY KEY,
                link TEXT NOT NULL,
                time TEXT NOT NULL,
                title TEXT NOT NULL,
                domain TEXT,
                board_name TEXT,
                board_id TEXT,
                board_type TEXT,
                author_name TEXT NOT NULL,
                author_id TEXT NOT NULL,
                author_ismod INTEGER NOT NULL,
                likes INTEGER NOT NULL,
                comments INTEGER NOT NULL,
                flair TEXT,
                author_awards TEXT,
                content TEXT,
                media TEXT
            )""")
            # list of tuples needed as cursor.executemary() input
            list_of_tuple = list(self.threads_df.itertuples(index=False, name=None))
            cur.executemany( # Use INSERT IGNORE not to have primary key confliction
                f"""INSERT OR IGNORE INTO reddit_thread_{self.subreddit} 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                list_of_tuple
            )
            conn.commit()
            print(f"SQL upload succeeded: {len(list_of_tuple)} records processed.")
        except Exception as e:
            print("SQL upload failed:", e)
        finally:
            conn.close() # prevents database locked error

    # Execute query on SQL database
    def query_sql(self, sql):
        conn = self.sql_connection()
        try:
            cur = conn.cursor()
            cur.execute(sql)
            
            records = cur.fetchall()
            columns_headers = [cols[0] for cols in cur.description]

            print(f"SQL query succeeded: {len(records)} records fetched.")
            return pd.DataFrame.from_records(data=records, columns=columns_headers)

        except Exception as e:
            print("SQL query failed:", e)
        finally:
            conn.close()

    def drop_sql_table(self, table):
        conn = self.sql_connection()
        try:
            cur = conn.cursor()
            cur.execute(f"DROP table {table};")
            print(f"SQL table dropped: {table}")

        except Exception as e:
            print("SQL table drop failed:", e)
        finally:
            conn.close()

    # Upload collected records into NoSQL database
    def upload_nosql(self):
        try:
            # Establish connection to NoSQL server
            es = Elasticsearch(self.ELASTIC_SERVER)
            es_index_name = f"reddit_thread_{self.subreddit}"

            # Loads json schema
            with open(self.NOSQL_MAPPING, 'r') as j:
                json_schema = json.loads(j.read())

            # Create index with predefined mappings if not exist
            if es.indices.exists(index=es_index_name):
                pass
            else:
                res = es.indices.create(index=es_index_name, **json_schema)
                print(res)

            # Insert data using Elasticsearch bulk API
            list_of_dicts = self.threads_df.to_dict('records')
            bulk_doc = [
                {
                    "_index": es_index_name,
                    "_source": a_record
                } for a_record in list_of_dicts
            ]
            res = helpers.bulk(es, bulk_doc)
            print(res)
            es.close()
        except Exception as e:
            print("Error occured in NoSQL operation: ", e)

    # Execute query on NoSQL database
    def query_nosql(self, query):
        try:
            es = Elasticsearch(self.ELASTIC_SERVER)
            es_index_name = f"reddit_thread_{self.subreddit}"

            res = es.search(index=es_index_name, query=query)
            print(f"Total {res['hits']['total']['value']} records returned.")
            es.close()
            return res['hits']['hits']
        except Exception as e:
            print("Error occured in NoSQL operation: ", e)
            return None

    def drop_nosql_index(self, index):
        try:
            es = Elasticsearch(self.ELASTIC_SERVER)

            res = es.indices.delete(
                index=index, 
                ignore=[400, 404] # ignores error when index does not exist
            )
            print(res)
        except Exception as e:
            print("Error occured in NoSQL operation: ", e)


if __name__ == '__main__':
    pass