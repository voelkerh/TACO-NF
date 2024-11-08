from taxdb import TaxDB

class TaxDBDump(TaxDB):
    def get_taxid_from_accession_number(self, accession):
        return ""