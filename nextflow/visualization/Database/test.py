import sqlite3

datenbank = 'database.db'
connection = sqlite3.connect(datenbank)

cursor = connection.cursor()
query = "SELECT name FROM sqlite_master WHERE type='table';"
cursor.execute(query)

tables = cursor.fetchall()
print("Tabellen in der Datenbank:")
for table in tables:
    table_name = table[0]
    print("Tabelle:", table_name)
    
    columns_query = f"PRAGMA table_info({table_name});"
    cursor.execute(columns_query)
    columns = cursor.fetchall()
    
    print("Spaltennamen:")
    for column in columns:
        print(column[1])
    
    first_row_query = f"SELECT * FROM {table_name} LIMIT 5;"
    cursor.execute(first_row_query)
    first_row = cursor.fetchall()
    
    print("Erste Zeile:")
    print(first_row)
    
    # count_query = f"SELECT COUNT(*) FROM {table_name};"
    # cursor.execute(count_query)
    # count = cursor.fetchone()[0]
    
    # print("Anzahl der Einträge:", count)
    # print()

connection.close()

def get_taxid_from_accession_number(accession_number):
    conn = sqlite3.connect(datenbank)
    cursor = conn.cursor()
    cursor.execute("SELECT taxid FROM accession2taxid WHERE accession = ?", (accession_number,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        return "NOT FOUND"

def get_parent(taxid):
    conn = sqlite3.connect(datenbank)
    cursor = conn.cursor()
    cursor.execute("SELECT parent_tax_id FROM nodes WHERE tax_id = ?", (taxid,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return "NOT FOUND"

def get_name(taxid):
    conn = sqlite3.connect(datenbank)
    cursor = conn.cursor()
    cursor.execute("SELECT name_txt FROM names WHERE tax_id = ?", (taxid,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return "NOT FOUND"
    
def get_rank(taxid):
    conn = sqlite3.connect(datenbank)
    cursor = conn.cursor()
    cursor.execute("SELECT rank FROM nodes WHERE tax_id = ?", (taxid,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return "NOT FOUND"
      
accession_number = 'NC_032111'
print(f"Accession: {accession_number}")
taxid = get_taxid_from_accession_number(accession_number)

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
        print(f"Keine weitere ParentID gefunden für TaxID {taxid}")
        break

def get_taxids_with_same_parent(parent_tax_id):
    conn = sqlite3.connect(datenbank)
    cursor = conn.cursor()
    cursor.execute("SELECT tax_id FROM nodes WHERE parent_tax_id = ?", (parent_tax_id,))
    results = cursor.fetchall()
    conn.close()
    
    if results:
        return [result[0] for result in results]
    else:
        return []

parent_tax_id_to_query = 1
taxids = get_taxids_with_same_parent(parent_tax_id_to_query)

print(f"Parent: {parent_tax_id_to_query} Name: {name} Rank: {rank}:")
for taxid in taxids:
    print(f"Children Taxid: {taxid} Name: {name} Rank: {rank} ")

#taxonomyDB Obejekt
# taxdbSqlite.py 

