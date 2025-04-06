"""
This script can be run after the manual execution of create_taxdb_file.py.
It ensures the correct build presenting contained tables and using sample queries.
"""

import os
import sqlite3

base_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(base_path)
database = os.path.join(parent_path, 'database.db')
connection = sqlite3.connect(database)

cursor = connection.cursor()
QUERY = "SELECT name FROM sqlite_master WHERE type='table';"
cursor.execute(QUERY)

tables = cursor.fetchall()
print("Tables in the database:")
for table in tables:
    table_name = table[0]
    print("\nTable:", table_name)

    COLUMNS_QUERY = f"PRAGMA table_info({table_name});"
    cursor.execute(COLUMNS_QUERY)
    columns = cursor.fetchall()

    print("\nColumn names:")
    for column in columns:
        print(column[1])

    FIRST_ROW_QUERY = f"SELECT * FROM {table_name} LIMIT 5;"
    cursor.execute(FIRST_ROW_QUERY)
    first_row = cursor.fetchall()

    print("\nFirst row:")
    print(first_row)
    print('\n-----')


def get_taxid_from_accession_number(query_accession_number):
    cursor.execute(
        "SELECT taxid FROM accession2taxid WHERE accession = ?", (query_accession_number,))
    result = cursor.fetchone()

    if result:
        return result[0]
    return "NOT FOUND"


def get_parent(query_taxid):
    cursor.execute(
        "SELECT parent_tax_id FROM nodes WHERE tax_id = ?", (query_taxid,))
    result = cursor.fetchone()

    if result:
        return result[0]
    return "NOT FOUND"


def get_name(query_taxid):
    cursor.execute(
        "SELECT name_txt FROM names WHERE tax_id = ?", (query_taxid,))
    result = cursor.fetchone()

    if result:
        return result[0]
    return "NOT FOUND"


def get_rank(query_taxid):
    cursor.execute("SELECT rank FROM nodes WHERE tax_id = ?", (query_taxid,))
    result = cursor.fetchone()

    if result:
        return result[0]
    return "NOT FOUND"


ACCESSION_NUMBER = 'NC_032111'
print(f"\nSample queries for accession: {ACCESSION_NUMBER}")
taxid = get_taxid_from_accession_number(ACCESSION_NUMBER)

print("\nTrace taxIDs from leave to root, requesting parent nodes")
while taxid is not None and taxid != "NOT FOUND":
    name = get_name(taxid)
    parent = get_parent(taxid)
    rank = get_rank(taxid)
    print(f"TaxID: {taxid}, Name: {name}, Rank: {rank}, ParentID: {parent}")

    if parent and parent != "NOT FOUND":
        taxid = parent
        if taxid == "1":
            break
    else:
        print(f"No more ParentIDs found for TaxID {taxid}")
        break


def get_taxids_with_same_parent(parent_tax_id):
    cursor.execute(
        "SELECT tax_id FROM nodes WHERE parent_tax_id = ?", (parent_tax_id,))
    results = cursor.fetchall()

    if results:
        return [result[0] for result in results]
    return []


PARENT_TAX_ID_TO_QUERY = 1
taxids = get_taxids_with_same_parent(PARENT_TAX_ID_TO_QUERY)

print('\n-----')

print("\nRequest all children from a given taxid - Example: taxid=1")

print(f"\nParent: {PARENT_TAX_ID_TO_QUERY} Name: {name} Rank: {rank}:")
for child_taxid in taxids:
    name = get_name(child_taxid)
    rank = get_rank(child_taxid)
    print(f"Children Taxid: {child_taxid} Name: {name} Rank: {rank} ")

connection.close()
