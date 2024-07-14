"""
init: helps to create db seamlessly.
======
The init.py file allow user to create database and tables.
- Database Name: crm.db
- table names:
  - bda: represents an individual who will handle given leads.
  - bda_payouts: It allow user to track data about their payouts
  - sales: Stores all the handled and unhandled leads.
"""


import sqlite3


def create_db():
    print("Setting up the things for you...")
    conn = sqlite3.connect("crm.db")  # Connect to the database "crm.db"

    cursor = conn.cursor()

    # create table named "bda" if it doesn't exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bda(
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                mobile TEXT UNIQUE,
                email TEXT NOT NULL UNIQUE
            )
    """)

    # create table named "bda_payouts" if it doesn't exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bda_payouts(
                id TEXT PRIMARY KEY,
                bda_id TEXT NOT NULL,
                paydate TEXT NOT NULL,
                remarks TEXT NOT NULL,
                amount INTEGER NOT NULL,
                FOREIGN KEY (bda_id) REFERENCES bda(id)               
            )
    """)

    # create table named "sales" if it doesn't exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales(
                    id TEXT PRIMARY KEY,
                    bda_id TEXT NOT NULL,
                    lead_name TEXT NOT NULL,
                    lead_mobile TEXT NOT NULL,
                    lead_result TEXT NOT NULL,
                    lead_status TEXT NOT NULL,
                    lead_date TEXT NOT NULL,
                    FOREIGN KEY(bda_id) REFERENCES bda(id)
            )
    """)

    # commit the changes after all queries are executed
    conn.commit()

    conn.close()  # close the connection - prevent resourece leaks
    print("Done...")

