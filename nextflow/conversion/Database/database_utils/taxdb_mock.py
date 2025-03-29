from taxdb import TaxDB

class TaxDBMock(TaxDB):

    def __init__(self):
        self.names = self.load_names_from_taxonomic_data()
        self.full_ranks = self.load_full_ranks_from_taxonomic_data()
        self.parents_taxid = self.load_parents_taxid_from_taxonomic_data()

    def get_taxid_from_accession_number(self, accession_number):
        # !!! hardcoded; TaxIDs für die zwei Referenzsequenzen: taxids = [67082, 687371]
        if accession_number == 'NC_032111':
            return 67082
        if accession_number == 'NC_014088':
            return 687371
    
    def load_names_from_taxonomic_data(self):
        names = {}
        with open('new_taxdump-2/names.dmp', 'r') as file:
            for line in file:
                parts = [part.strip() for part in line.split('|')]
                if parts[3] == 'scientific name':
                    names[parts[0]] = parts[1]
        return names
    
    def load_full_ranks_from_taxonomic_data(self):
        full_ranks = {}
        with open('new_taxdump-2/nodes.dmp', 'r') as file:
            for line in file:
                parts = [part.strip() for part in line.split('|')]
                full_ranks[parts[0]] = parts[2]
        return full_ranks

    def load_parents_taxid_from_taxonomic_data(self):
        parents_taxid = {}
        with open('new_taxdump-2/nodes.dmp', 'r') as file:
            for line in file:
                parts = [part.strip() for part in line.split('|')]
                parents_taxid[parts[0]] = parts[1]
        return parents_taxid

    def get_name_from_taxonomic_data(self, taxid):
        return self.names.get(str(taxid), "NOT FOUND")

    def get_parent_taxid_from_taxonomic_data(self, taxid):
        return self.parents_taxid.get(str(taxid), None)

    def get_full_rank_from_taxonomic_data(self, taxid):
        return self.full_ranks.get(str(taxid), '?')

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
        # default '?' für 'no rank'
        return rank_mapping.get(rank.lower(), '?')  
    
