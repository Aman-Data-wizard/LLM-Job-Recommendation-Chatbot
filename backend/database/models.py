import sqlite3
from backend.database.db import get_connection
import pandas as pd

def create_jobs_table():
     conn = get_connection()
     cursor = conn.cursor()
     cursor.execute('''
           CREATE TABLE IF NOT EXISTS jobs (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT,
               company TEXT,
               location TEXT,
               description TEXT,
               source TEXT,
               fetched_at TEXT
               )
     ''')
     conn.commit()
     conn.close()
# We used an auto-increment primary key and normalized job attributes

def insert_jobs(jobs):
     
     conn = get_connection()
     cursor = conn.cursor()
     
     for job in jobs:
         cursor.execute('''
             INSERT INTO jobs (
                  title,
                  company,
                  location, 
                  description, 
                  source,
                  fetched_at
               )
             VALUES (?, ?, ?, ?, ?, datetime('now'))
         ''', (
               job.get("title"),
               job.get("company"),
               job.get("location"),
               job.get("description"),
               job.get("source", "Adzuna")
         ))
         
     conn.commit()
     conn.close()

def load_jobs_from_db():
     conn = get_connection()
     df = pd.read_sql_query("SELECT * FROM jobs", conn)
     conn.close()
     
     print("Debug: total jobs in DB =", len(df))
     print(df.head())
     return df
     
     