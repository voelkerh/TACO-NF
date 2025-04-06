"""
This script has to be executed manually before running the pipeline.
It creates a taxonomy database based on previous downloads (/new_taxdump and /nucl_gb).
The database.db will be stored in the parent directory for use by converter scripts.
At the first run use option "create" als command line argument.
It can later be rebuilt with option "update".

The database translates SRA accession IDs to taxIDs and allows
retrieval of the nodes and names information.
"""

import os
import argparse
import sqlite3
import csv
import pandas as pd

base_path = os.path.dirname(os.path.abspath(__file__))
# move one directory up to save db where needed
parent_path = os.path.dirname(base_path)
db_path = os.path.join(parent_path, 'database.db')


def create_accession2taxid_table(db_file, csv_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accession2taxid (
                accession TEXT,
                taxid TEXT
            )
        ''')

        with open(csv_file, 'r', encoding='UTF-8') as f:
            reader = csv.reader(f)
            for row in reader:
                cursor.execute('''
                            INSERT INTO accession2taxid(accession, taxid) VALUES(?, ?)
                            ''', row)

        conn.commit()

    except FileNotFoundError as e:
        print(f"[ERROR] CSV file not found: {e}")
    except sqlite3.DatabaseError as e:
        print(f"[ERROR] Database error: {e}")
    except csv.Error as e:
        print(f"[ERROR] CSV parsing error: {e}")

    finally:
        conn.close()


def convert_nodes_dmp_to_csv():
    nodes_file = os.path.join(base_path, 'new_taxdump', 'nodes.dmp')
    df = pd.read_csv(nodes_file, sep='|', header=None, engine='python')
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    print(f"Number of columns in DataFrame: {df.shape[1]}")

    column_names = ['tax_id', 'parent_tax_id', 'rank', 'embl_code', 'division_id',
                    'inherited_div_flag', 'genetic_code_id', 'inherited_GC_flag',
                    'mitochondrial_genetic_code_id', 'inherited_MGC_flag', 'GenBank_hidden_flag',
                    'hidden_subtree_root_flag', 'comments', 'plastid_genetic_code_id',
                    'inherited_PGC_flag', 'specified_species',
                    'hydrogenosome_genetic_code_id', 'inherited_HGC_flag']

    if len(column_names) == df.shape[1] - 1:
        df.columns = column_names + ['extra']
    else:
        df.columns = column_names

    print(df.head())

    output_path = os.path.join(base_path, 'nodes.csv')
    df.to_csv(output_path, index=False, sep=';')


def filter_columns_in_nodes_csv():
    nodes_file = os.path.join(base_path, 'nodes.csv')
    if not os.path.exists(nodes_file):
        raise FileNotFoundError(f"{nodes_file} not found.")
    df = pd.read_csv(nodes_file, sep=';')

    columns_to_keep = ['tax_id', 'parent_tax_id', 'rank', 'embl_code', 'division_id',
                       'inherited_div_flag', 'genetic_code_id', 'inherited_GC_flag',
                       'mitochondrial_genetic_code_id', 'inherited_MGC_flag', 'GenBank_hidden_flag',
                       'hidden_subtree_root_flag', 'comments', 'plastid_genetic_code_id',
                       'inherited_PGC_flag', 'specified_species',
                       'hydrogenosome_genetic_code_id', 'inherited_HGC_flag']

    missing_columns = [col for col in columns_to_keep if col not in df.columns]
    if missing_columns:
        print(
            f"The following columns are absent in the csv file: {', '.join(missing_columns)}")

    for col in columns_to_keep:
        if col in df.columns:
            df[col].fillna('unknown', inplace=True)

    df_filtered = df[columns_to_keep]
    df_filtered.to_csv('nodes_filtered.csv', index=False, sep=';')

    print(
        f"This filtered nodes file contains the required columns: {nodes_file}")


def convert_names_dmp_to_csv():
    names_file = os.path.join(base_path, 'new_taxdump', 'names.dmp')

    df = pd.read_csv(names_file, sep='|', header=None, engine='python')
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    print(f"Number of columns in DataFrame: {df.shape[1]}")

    column_names = ['tax_id', 'name_txt', 'unique name', 'name class']
    if len(column_names) == df.shape[1] - 1:
        df.columns = column_names + ['extra']
    else:
        df.columns = column_names

    print(df.head())

    output_path = os.path.join(base_path, 'names.csv')
    df.to_csv(output_path, index=False, sep=';')


def filter_columns_in_names_csv():
    names_file = os.path.join(base_path, 'names.csv')
    if not os.path.exists(names_file):
        raise FileNotFoundError(f"{names_file} not found.")
    df = pd.read_csv(names_file, sep=';')

    columns_to_keep = ['tax_id', 'name_txt', 'unique name', 'name class']
    missing_columns = [col for col in columns_to_keep if col not in df.columns]
    if missing_columns:
        print(
            f"The following columns are absent in the csv file: {', '.join(missing_columns)}")

    for col in columns_to_keep:
        if col in df.columns:
            df[col].fillna('unknown', inplace=True)

    df_filtered = df[columns_to_keep]
    df_filtered.to_csv('names_filtered.csv', index=False, sep=';')

    print(
        f"This filtered nodes file contains the required columns: {names_file}")


def table_exists(cursor, table_name):
    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None


def create_table_from_csv(db_filename, table_name, csv_filename):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    if table_exists(cursor, table_name):
        print(f"Table {table_name} already exists. Connection will be closed.")
        conn.close()
        return

    with open(csv_filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        headers = next(reader)
        column_info = []
        for col in headers:
            col = col.strip().replace(' ', '_').replace('-', '_')
            if not col.isidentifier():
                col = f'col_{col}'
            column_info.append(col + ' TEXT')

    create_table_query = f"CREATE TABLE {table_name} ({', '.join(column_info)})"
    cursor.execute(create_table_query)
    conn.commit()

    with open(csv_filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        next(reader)
        for row in reader:
            insert_query = f"INSERT INTO {table_name} VALUES ({','.join(['?']*len(row))})"
            cursor.execute(insert_query, row)
        conn.commit()

    conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Create database.db to translate accession2taxid")
    parser.add_argument("action", choices=[
                        "create", "update"], help="Chose 'create' or 'update'.")

    args = parser.parse_args()
    names_csv_filename = os.path.join(base_path, 'names_filtered.csv')
    nodes_csv_filename = os.path.join(base_path, 'nodes_filtered.csv')
    input_file = os.path.join(base_path, 'nucl_gb/nucl_gb.accession2taxid')
    output_file = os.path.join(base_path, 'new_nucl_gb.accession2taxid.csv')

    if args.action == "create":
        if os.path.exists(db_path):
            print(f"{db_path} already exists.")
            create_table_from_csv(db_path, 'names', names_csv_filename)
            create_table_from_csv(db_path, 'nodes', nodes_csv_filename)

        else:
            print(f"{db_path} was not found. Create database.db file.")
            convert_nodes_dmp_to_csv()
            convert_names_dmp_to_csv()
            filter_columns_in_nodes_csv()
            filter_columns_in_names_csv()

            with open(input_file, 'r', encoding='UTF-8') as f:
                with open(output_file, 'w', newline='', encoding='UTF-8') as new_file:
                    csv_writer = csv.writer(new_file)
                    for line in f:
                        columns = line.strip().split('\t')
                        selected_columns = [columns[0], columns[2]]
                        csv_writer.writerow(selected_columns)

            create_accession2taxid_table(db_path, output_file)
            create_table_from_csv(db_path, 'names', names_csv_filename)
            create_table_from_csv(db_path, 'nodes', nodes_csv_filename)

    elif args.action == "update":
        if os.path.exists(db_path):
            os.remove(db_path)
            print('Database file removed')
            print(f"{db_path} will be recreated...")
            convert_nodes_dmp_to_csv()
            convert_names_dmp_to_csv()
            filter_columns_in_nodes_csv()
            filter_columns_in_names_csv()

            with open(input_file, 'r', encoding='UTF-8') as f:
                with open(output_file, 'w', newline='', encoding='UTF-8') as new_file:
                    csv_writer = csv.writer(new_file)
                    for line in f:
                        columns = line.strip().split('\t')
                        selected_columns = [columns[0], columns[2]]
                        csv_writer.writerow(selected_columns)

            create_accession2taxid_table(db_path, output_file)
            create_table_from_csv(db_path, 'names', names_csv_filename)
            create_table_from_csv(db_path, 'nodes', nodes_csv_filename)


if __name__ == "__main__":
    main()
