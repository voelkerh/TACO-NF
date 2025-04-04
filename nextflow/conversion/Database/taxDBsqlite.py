import sqlite3
from .taxdb import TaxDB


class TaxDBsqlite(TaxDB):
    """Representation of the internal taxonomic database providing functions for data retrieval."""

    def __init__(self, sqlite_file):
        self.sqlite_file = sqlite_file

    def load_taxid_from_accession_number(self, accession):
        conn = sqlite3.connect(self.sqlite_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT taxid FROM accession2taxid WHERE accession = ?", (accession,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]

        return "NOT FOUND"

    def load_names_from_taxonomic_data(self, taxid):
        conn = sqlite3.connect(self.sqlite_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name_txt FROM names WHERE tax_id = ? AND name_class = 'scientific name'",
            (taxid,)
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]

        return "NOT FOUND"

    def load_full_ranks_from_taxonomic_data(self, taxid):
        conn = sqlite3.connect(self.sqlite_file)
        cursor = conn.cursor()
        cursor.execute("SELECT rank FROM nodes WHERE tax_id = ?", (taxid,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]

        return "NOT FOUND"

    def load_parents_taxid_from_taxonomic_data(self, taxid):
        conn = sqlite3.connect(self.sqlite_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT parent_tax_id FROM nodes WHERE tax_id = ?", (taxid,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]

        return "NOT FOUND"

    def get_taxid_from_accession_number(self, accession):
        return self.load_taxid_from_accession_number(accession)

    def get_name_from_taxonomic_data(self, taxid):
        return self.load_names_from_taxonomic_data(taxid)

    def get_parent_taxid_from_taxonomic_data(self, taxid):
        return self.load_parents_taxid_from_taxonomic_data(taxid)

    def get_full_rank_from_taxonomic_data(self, taxid):
        return self.load_full_ranks_from_taxonomic_data(taxid)

    def get_rank_code_from_full_rank(self, rank):
        rank_mapping = {
            'unclassified': 'U',
            'root': ' ',
            'domain': 'D',
            'superkingdom': ' ',
            'kingdom': 'K',
            'phylum': 'P',
            'class': 'C',
            'order': 'O',
            'family': 'F',
            'genus': 'G',
            'species': 'S'
        }
        return rank_mapping.get(rank.lower(), '?')
