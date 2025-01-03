import os
import sqlite3
import csv
import pandas as pd
import argparse

# Muss refactored werden TODO
# store dir -> gucke https://www.nextflow.io/docs/latest/reference/process.html#storedir
# prozess 1 -> dmps runterladen wenn nicht vorhanden (Kein Input, läuft immer) entpackt sie. Gibt 3 dumps aus
# prozess 2 -> Nimmt 3 dmps (OUTPUT Channle von P1 als input für P2) verwendet dabei store dir
#        rufe die datenbank auf mit create zeil 158
#           liest die ganzen dmps ein und erstellt die sqlite db (mit sotre dir, damit wenn bereits vorhanden übersprungen wird)
#

# Datenbankpfad
db_file = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/database.db'

def create_db(db_file, csv_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS accession2taxid (
                   accession TEXT,
                   taxid TEXT
                   )
                   ''')

    with open(csv_file, 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            cursor.execute('''
                           INSERT INTO accession2taxid(accession, taxid) VALUES(?, ?)
                           ''', row)

    conn.commit()
    conn.close() 

def nodesToCSV():
    nodes_file = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/new_taxdump/nodes.dmp'
    df = pd.read_csv(nodes_file, sep='|', header=None, engine='python')
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    print(f"Anzahl der Spalten im DataFrame: {df.shape[1]}")

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

    output_path = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/nodes.csv'
    df.to_csv(output_path, index=False, sep=';')

def cut_nodes():
    nodes_file = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/nodes.csv'
    df = pd.read_csv(nodes_file, sep=';')

    columns_to_keep = ['tax_id', 'parent_tax_id', 'rank', 'embl_code', 'division_id', 
                       'inherited_div_flag', 'genetic_code_id', 'inherited_GC_flag', 
                       'mitochondrial_genetic_code_id', 'inherited_MGC_flag', 'GenBank_hidden_flag', 
                       'hidden_subtree_root_flag', 'comments', 'plastid_genetic_code_id', 
                       'inherited_PGC_flag', 'specified_species', 
                       'hydrogenosome_genetic_code_id', 'inherited_HGC_flag']

    missing_columns = [col for col in columns_to_keep if col not in df.columns]
    if missing_columns:
        print(f"Die folgenden Spalten fehlen in der CSV-Datei: {', '.join(missing_columns)}")

    for col in columns_to_keep:
        if col in df.columns:
            df[col].fillna('unknown', inplace=True)

    df_filtered = df[columns_to_keep]
    df_filtered.to_csv(nodes_file, index=False, sep=';')

    print(f"Die CSV-Datei wurde mit den ausgewählten Spalten überschrieben: {nodes_file}")

def namesToCSV():
    names_file = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/new_taxdump/names.dmp'
    df = pd.read_csv(names_file, sep='|', header=None, engine='python')
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    print(f"Anzahl der Spalten im DataFrame: {df.shape[1]}")

    column_names = ['tax_id', 'name_txt', 'unique name', 'name class']
    if len(column_names) == df.shape[1] - 1:
        df.columns = column_names + ['extra']
    else:
        df.columns = column_names

    print(df.head())

    output_path = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/names.csv'
    df.to_csv(output_path, index=False, sep=';')

def cut_names():
    names_file = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/names.csv'
    df = pd.read_csv(names_file, sep=';')

    columns_to_keep = ['tax_id', 'name_txt', 'unique name', 'name class']
    missing_columns = [col for col in columns_to_keep if col not in df.columns]
    if missing_columns:
        print(f"Die folgenden Spalten fehlen in der CSV-Datei: {', '.join(missing_columns)}")

    for col in columns_to_keep:
        if col in df.columns:
            df[col].fillna('unknown', inplace=True)

    df_filtered = df[columns_to_keep]
    df_filtered.to_csv(names_file, index=False, sep=';')

    print(f"Die CSV-Datei wurde mit den ausgewählten Spalten überschrieben: {names_file}")

def table_exists(cursor, table_name):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None

def create_table_from_csv(db_filename, table_name, csv_filename):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    
    if table_exists(cursor, table_name):
        print(f"Tabelle {table_name} existiert bereits. Der Code wird nicht ausgeführt.")
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
    parser = argparse.ArgumentParser(description="Datenbank-Erstellungs- und Löschprogramm.")
    parser.add_argument("action", choices=["create", "update"], help="Die Aktion, die ausgeführt werden soll: 'create' oder 'update'.")

    args = parser.parse_args()

    if args.action == "create":
        if os.path.exists(db_file):
            print(f"{db_file} wurde bereits gefunden")
            names_table_name = 'names'
            names_csv_filename = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/names.csv'  
            create_table_from_csv(db_file, names_table_name, names_csv_filename)

            nodes_table_name = 'nodes'
            nodes_csv_filename = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/nodes.csv'
            create_table_from_csv(db_file, nodes_table_name, nodes_csv_filename)
                
        else:
            print(f"{db_file} wurde nicht gefunden. Erstelle die Datenbank...")
            nodesToCSV()
            namesToCSV()
            cut_nodes()
            cut_names()

            input_file = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/nucl_gb.accession2taxid'
            output_file = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/new_nucl_gb.accession2taxid.csv'

            with open(input_file, 'r') as f:
                with open(output_file, 'w', newline='') as new_file:
                    csv_writer = csv.writer(new_file)
                    for line in f:
                        columns = line.strip().split('\t')
                        selected_columns = [columns[0], columns[2]]
                        csv_writer.writerow(selected_columns)

            csv_file = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/new_nucl_gb.accession2taxid.csv'
            create_db(db_file, csv_file)
            create_table_from_csv(db_file, 'names', '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/names.csv')
            create_table_from_csv(db_file, 'nodes', '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/nodes.csv')

    elif args.action == "update":
        if os.path.exists(db_file):
            os.remove(db_file)
            print('Datenbank entfernt')
            print(f"{db_file} wird neu erstellt...")
            nodesToCSV()
            namesToCSV()
            cut_nodes()
            cut_names()

            input_file = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/nucl_gb.accession2taxid'
            output_file = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/new_nucl_gb.accession2taxid.csv'

            with open(input_file, 'r') as f:
                with open(output_file, 'w', newline='') as new_file:
                    csv_writer = csv.writer(new_file)
                    for line in f:
                        columns = line.strip().split('\t')
                        selected_columns = [columns[0], columns[2]]
                        csv_writer.writerow(selected_columns)

            csv_file = '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/new_nucl_gb.accession2taxid.csv'
            create_db(db_file, csv_file)
            create_table_from_csv(db_file, 'names', '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/names.csv')
            create_table_from_csv(db_file, 'nodes', '/Users/benjamin/Desktop/Uni/4.Semester/Projektstudium/nodes.csv')

if __name__ == "__main__":
    main()
