#!/usr/bin/python3

import sys
import sqlite3

from TaxDB import TaxDB 

# Positionalparameter: SAM Datei, Gesamtzahl der Reads
sam_file = sys.argv[1]
total_reads = int(sys.argv[2])
database_path = "database.db"

class SAMConverter:

    def __init__(self, taxdb : TaxDB):
        self.taxdb = taxdb

    def read_sam_file_to_lines(self, sam_file):
        with open(sam_file, 'r') as file:
            return file.readlines()

    def extract_accession_numbers_from_sam_lines(self, lines):
        accession_numbers_from_file = []
        for line in lines:
            if line.startswith('@SQ'):
                accession_number = line.split(':')[1].split('.')[0]
                if accession_number not in accession_numbers_from_file:
                    accession_numbers_from_file.append(accession_number)
        return accession_numbers_from_file

    def count_alignments_per_accession_number_from_lines(self, lines, accession_numbers_from_file):
        accession_counts = {}
        for accession_number in accession_numbers_from_file:
            accession_counts[accession_number] = 0
        for line in lines:
            if not(line.startswith('@')):
                line_accession = line.split('\t')[2].split('.')[0]
                accession_counts[line_accession] += 1
        return accession_counts

    def count_alignments_per_taxid_from_lines(self, lines, accession_numbers_from_file):
        accession_counts = self.count_alignments_per_accession_number_from_lines(lines, accession_numbers_from_file)
        accession_counts_by_taxid = {}

        for accession_number, count in accession_counts.items():
            taxid = self.get_taxid_from_accession_number(accession_number)
            if taxid == "NOT FOUND":
                continue
            if taxid in accession_counts_by_taxid:
                accession_counts_by_taxid[taxid] += count
            else:
                accession_counts_by_taxid[taxid] = count
        return accession_counts_by_taxid

    def calculate_classified_reads(self, accession_counts):
        classified_reads = 0
        for accession in accession_counts:
            classified_reads += accession_counts[accession]
        return classified_reads

    def calculate_unclassified_reads(self, accession_counts):
        return total_reads - self.calculate_classified_reads(accession_counts)

    def calculate_percentage_of_reads(self, number_of_reads):
        return round((number_of_reads / total_reads * 100), 2)

    def load_names_from_taxonomic_data(self, taxid):
        return self.taxdb.load_names_from_taxonomic_data(taxid)

    def load_full_ranks_from_taxonomic_data(self, rank):
        return self.taxdb.load_full_ranks_from_taxonomic_data(rank)

    def load_parents_taxid_from_taxonomic_data(self, taxid):
        return self.taxdb.load_parents_taxid_from_taxonomic_data(taxid)
        
    def get_taxid_from_accession_number(self, accession_number):
        return self.taxdb.get_taxid_from_accession_number(accession_number)

    def get_name_from_taxonomic_data(self, taxid):
        return self.taxdb.get_name_from_taxonomic_data(taxid)

    def get_parent_taxid_from_taxonomic_data(self, taxid):
        return self.taxdb.get_parent_taxid_from_taxonomic_data(taxid)

    def get_full_rank_from_taxonomic_data(self, taxid):
        return self.taxdb.get_full_rank_from_taxonomic_data(taxid)

    def get_rank_code_from_full_rank(self, rank):
        return self.taxdb.get_rank_code_from_full_rank(rank)                       

    class Node:
        def __init__(self, name, taxid, rank = '?', parent = None, cumulative_reads = 0):
            self.name = name
            self.taxid = taxid
            self.rank = rank
            self.parent = parent
            self.children = []
            self.cumulative_reads = cumulative_reads

        def add_child(self, child):
            existing_child = self.get_child(child.taxid)
            if existing_child:
                return existing_child
            else:
                self.children.append(child)
                child.parent = self
                return child

        def get_child(self, taxid):
            for child in self.children:
                if child.taxid == taxid:
                    return child
            return None

        def has_child(self, taxid):
            return any(child.taxid == taxid for child in self.children)
        
        def __eq__(self, other):
            return self.taxid == other.taxid

    def build_branch(self, taxid):
        branch = []
        while taxid and taxid != '1': # Wurzel erreicht
            parent_taxid = self.get_parent_taxid_from_taxonomic_data(taxid)
            name = self.get_name_from_taxonomic_data(taxid)
            rank = self.get_full_rank_from_taxonomic_data(taxid)
            rank_code = self.get_rank_code_from_full_rank(rank)
            if rank_code == '?' and parent_taxid is not None and parent_taxid != '1':
                parent_rank_code = self.get_rank_code_from_full_rank(self.get_full_rank_from_taxonomic_data(parent_taxid))
                rank_code = '1' if parent_rank_code == ' ' else parent_rank_code + '1'
            node = self.Node(name, taxid, rank_code, parent_taxid)
            branch.insert(0, node) # Umgekehrte Reihenfolge (von Wurzel zu Blatt)
            taxid = parent_taxid
        return branch

    def build_tree(self, accession_numbers_from_file, accession_counts_by_taxid):
        root = self.Node('root', 1, ' ', None, 0)
        for accession_number in accession_numbers_from_file:
            taxid = self.taxdb.get_taxid_from_accession_number(accession_number)
            if taxid == "NOT FOUND":
                continue
            reads_for_current_taxid = accession_counts_by_taxid.get(taxid, 0)
            branch = self.build_branch(taxid) # jeweils Wurzel bis Blatt
            current_node_in_tree = root # Beginne an der Wurzel
            current_node_in_tree.cumulative_reads += reads_for_current_taxid # Addiere die Reads für die Wurzel
            add_new_nodes_to_tree = False
            for node_in_branch in branch: # Durchlaufe die Knoten des Zweiges
                if add_new_nodes_to_tree:
                        new_node = self.Node(node_in_branch.name, node_in_branch.taxid, node_in_branch.rank, current_node_in_tree, reads_for_current_taxid)
                        current_node_in_tree = current_node_in_tree.add_child(new_node)
                else:
                    child = current_node_in_tree.get_child(node_in_branch.taxid) # Prüft, ob nächster Knoten des Zweiges bereits im Baum ist
                    if child:
                        child.cumulative_reads += reads_for_current_taxid # Addiere die Reads des Zweiges zu bestehendem Knoten
                        current_node_in_tree = child
                    else:
                        new_node = self.Node(node_in_branch.name, node_in_branch.taxid, node_in_branch.rank, current_node_in_tree, reads_for_current_taxid)
                        current_node_in_tree = current_node_in_tree.add_child(new_node)
                        add_new_nodes_to_tree = True
        return root

    def write_data_for_nodes_in_branch(self, file, node, accession_counts_by_taxid, level=0):
        indent = '  ' * level
        reads_per_taxid = accession_counts_by_taxid.get(node.taxid, 0)
        percentage = self.calculate_percentage_of_reads(node.cumulative_reads)
        file.write(f"{percentage}\t{node.cumulative_reads}\t{reads_per_taxid}\t{node.rank}\t{node.taxid}\t{indent}{node.name}\n")
        for child in node.children:
            self.write_data_for_nodes_in_branch(file, child, accession_counts_by_taxid, level + 1)

    def create_output_file(self, tree, accession_counts_by_taxid, unclassified_reads, percentage_of_unclassified_reads):
        with open('samtokraken.txt', 'w') as file:
            file.write(f"{percentage_of_unclassified_reads}\t{unclassified_reads}\t{unclassified_reads}\tU\t0\tunclassified\n")
            self.write_data_for_nodes_in_branch(file, tree, accession_counts_by_taxid)

from taxDBsqlite import TaxDBsqlite

taxdb_instance = TaxDBsqlite(database_path)
converter = SAMConverter(taxdb_instance)
lines = converter.read_sam_file_to_lines(sam_file)
accession_numbers = converter.extract_accession_numbers_from_sam_lines(lines)
accession_counts_by_taxid = converter.count_alignments_per_taxid_from_lines(lines, accession_numbers)
classified_reads = converter.calculate_classified_reads(accession_counts_by_taxid)
unclassified_reads = converter.calculate_unclassified_reads(accession_counts_by_taxid)
percentage_of_unclassified_reads = converter.calculate_percentage_of_reads(unclassified_reads)
tree = converter.build_tree(accession_numbers, accession_counts_by_taxid)
converter.create_output_file(tree, accession_counts_by_taxid, unclassified_reads, percentage_of_unclassified_reads)
