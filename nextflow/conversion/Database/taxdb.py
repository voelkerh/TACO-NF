"""
Definition of abstract class for internal taxonomy database
allows for customized adaption of database behaviour.
"""

from abc import ABC, abstractmethod


class TaxDB(ABC):
    """Abstract class defining retrieval methods for internal taxonomy database."""

    def __init__(self):
        pass

    @abstractmethod
    def load_taxid_from_accession_number(self, accession):
        return ""

    @abstractmethod
    def load_names_from_taxonomic_data(self, taxid):
        return ""

    @abstractmethod
    def load_full_ranks_from_taxonomic_data(self, taxid):
        return ""

    @abstractmethod
    def load_parents_taxid_from_taxonomic_data(self, taxid):
        return ""

    @abstractmethod
    def get_taxid_from_accession_number(self, accession):
        return ""

    @abstractmethod
    def get_name_from_taxonomic_data(self, taxid):
        return ""

    @abstractmethod
    def get_parent_taxid_from_taxonomic_data(self, taxid):
        return ""

    @abstractmethod
    def get_full_rank_from_taxonomic_data(self, taxid):
        return ""

    @abstractmethod
    def get_rank_code_from_full_rank(self, rank):
        return ""
