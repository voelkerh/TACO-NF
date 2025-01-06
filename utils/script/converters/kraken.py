import os
import sys
from Database.taxDBsqlite import TaxDBsqlite
from script.abstract_converter import AbstractConverter
import sqlite3
from Database.taxdb import TaxDB

database_path = "Database/database.db"

class KrakenConverter(AbstractConverter):
    
    def __init__(self, taxdb: TaxDB):
        self.taxdb = taxdb
    
    
    def can_convert(self, filename: str) -> bool:
        with open(filename, 'r') as f:
            header = f.readline().strip
            try:
                root= f.readline().strip().split("\t")[5]
                if root == "root":
                    return True     
            except:
                return False
   

    def convert(self, filename: str) -> str:
      
        if not self.can_convert(filename):
            raise ValueError(f"Die Datei {filename} kann nicht konvertiert werden. Nur .gt-Dateien sind erlaubt.")
        
     
        with open(filename, 'r') as infile:
            lines = infile.readlines()

        for i in range(2, len(lines)):  
            try:
                line = lines[i]
                
                # Zeile in Spalten splitten und die Leerzeichen zwischen tax_id und name zählen
                parts = line.split('\t')
                perc_reads, read_number, reads, rank, tax_id, name = parts[:6]

                # Entfernen der führenden und abschließenden Leerzeichen aus tax_id und name
                tax_id = tax_id.strip()
                name = name.strip()

                # Zählen der Leerzeichen zwischen tax_id und name
                spaces_between = len(parts[5]) - len(parts[5].lstrip())

                # Überprüfen, ob der Name mit dem aus der Datenbank übereinstimmt
                updated_name = self.get_name_from_taxonomic_data(tax_id)
                if updated_name != name:
                 
                    name = updated_name

                lines[i] = f"{perc_reads}\t{read_number}\t{reads}\t{rank}\t{tax_id}\t{' ' * spaces_between}{name}\n"

            except ValueError as e:
                # Fehlerbehandlung, wenn Zeile nicht korrekt ist
                print(f"Error processing line: {line.strip()} - {e}")
                continue
        
        self.create_output_file(lines)
            
        return "Conversion successful. Output created in 'results/kraken.report'."

    def create_output_file(self, lines):
        script_directory = os.path.dirname(os.path.abspath(__file__))

        parent_directory = os.path.dirname(script_directory)

        results_directory = os.path.join(parent_directory, 'results')
        if not os.path.exists(results_directory):
            os.makedirs(results_directory)
        output_file = os.path.join(results_directory, f"kraken.report")

        with open(output_file, 'w') as file:
            file.writelines(lines)



    
    def load_names_from_taxonomic_data(self, taxid):
        return self.taxdb.load_names_from_taxonomic_data(taxid)
    
    def get_name_from_taxonomic_data(self, taxid):
        return self.taxdb.get_name_from_taxonomic_data(taxid)       
        

if __name__ == '__main__':
    pass
    # taxdb_instance = TaxDBsqlite(database_path)
    # c = KrakenConverter(taxdb_instance)
    # print(c.convert("c.k2d"))

    
    