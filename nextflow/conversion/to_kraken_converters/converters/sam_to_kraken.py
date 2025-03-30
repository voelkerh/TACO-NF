from Database.taxdb import TaxDB
from to_kraken_converters.abstract_converter import AbstractConverter


class SAMConverter(AbstractConverter):

    def __init__(self, taxdb: TaxDB):
        self.taxdb = taxdb

    def can_convert(self, filename):

        with open(filename, 'r') as f:
            lines = f.readlines()

        header_lines = [line for line in lines if line.startswith("@")]
        has_hd = any(line.startswith("@HD") for line in header_lines)
        has_sq = any(line.startswith("@SQ") for line in header_lines)
        has_alignment = any(line.startswith("SRR") for line in lines)

        return has_hd and has_sq and has_alignment

    def convert(self, filename: str, output_filename: str) -> str:
        if not self.can_convert(filename):
            raise ValueError(
                f"The file {filename} cannot be converted. It is not a SAM file.")

        lines = self.read_sam_file_to_lines(filename)
        total = self.count_numreads(lines)
        accession_numbers = self.extract_accession_numbers_from_sam_lines(
            lines)
        accession_counts_by_taxid = self.count_alignments_per_taxid_from_lines(
            lines, accession_numbers)
        unclassified_reads = self.calculate_unclassified_reads(
            accession_counts_by_taxid, total)
        percentage_of_unclassified_reads = self.calculate_percentage_of_reads(
            unclassified_reads, total)

        tree = self.build_tree(accession_numbers, accession_counts_by_taxid)
        self.create_output_file(tree, accession_counts_by_taxid, unclassified_reads, percentage_of_unclassified_reads,
                                total, output_filename)

        return "Conversion successful (SAM to kraken)."

    def read_sam_file_to_lines(self, sam_file: str) -> list:
        with open(sam_file, 'r') as file:
            return file.readlines()

    def count_numreads(self, lines: list) -> int:
        return sum(1 for line in lines if not line.startswith('@'))

    def extract_accession_numbers_from_sam_lines(self, lines: list) -> list:
        accession_numbers_from_file = []
        for line in lines:
            if line.startswith('@SQ'):
                accession_number = line.split(':')[1].split('.')[0]
                if accession_number not in accession_numbers_from_file:
                    accession_numbers_from_file.append(accession_number)
        return accession_numbers_from_file

    def count_alignments_per_accession_number_from_lines(self, lines: list, accession_numbers_from_file: list) -> dict:
        accession_counts = {}
        for accession_number in accession_numbers_from_file:
            accession_counts[accession_number] = 0
        for line in lines:
            if not (line.startswith('@')):
                line_accession = line.split('\t')[2].split('.')[0]
                if line_accession == '*':
                    continue
                accession_counts[line_accession] += 1
        return accession_counts

    def count_alignments_per_taxid_from_lines(self, lines: list, accession_numbers_from_file: list) -> dict:
        accession_counts = self.count_alignments_per_accession_number_from_lines(
            lines, accession_numbers_from_file)
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

    def calculate_classified_reads(self, accession_counts: dict) -> int:
        return sum(accession_counts.values())

    def calculate_unclassified_reads(self, accession_counts, total_reads):
        return total_reads - self.calculate_classified_reads(accession_counts)

    def calculate_percentage_of_reads(self, number_of_reads, total_reads):
        return round((number_of_reads / total_reads * 100), 2)

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
        def __init__(self, name, taxid, rank='?', parent=None, cumulative_reads=0):
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
        while taxid and taxid != '1':  # Wurzel erreicht
            parent_taxid = self.get_parent_taxid_from_taxonomic_data(taxid)
            name = self.get_name_from_taxonomic_data(taxid)
            rank = self.get_full_rank_from_taxonomic_data(taxid)
            rank_code = self.get_rank_code_from_full_rank(rank)
            if rank_code == '?' and parent_taxid is not None and parent_taxid != '1':
                parent_rank_code = self.get_rank_code_from_full_rank(
                    self.get_full_rank_from_taxonomic_data(parent_taxid))
                rank_code = '1' if parent_rank_code == ' ' else parent_rank_code + '1'
            node = self.Node(name, taxid, rank_code, parent_taxid)
            # Umgekehrte Reihenfolge (von Wurzel zu Blatt)
            branch.insert(0, node)
            taxid = parent_taxid
        return branch

    def build_tree(self, accession_numbers_from_file, accession_counts_by_taxid):
        root = self.Node('root', 1, ' ', None, 0)
        for accession_number in accession_numbers_from_file:
            taxid = self.taxdb.get_taxid_from_accession_number(
                accession_number)
            if taxid == "NOT FOUND":
                continue
            reads_for_current_taxid = accession_counts_by_taxid.get(taxid, 0)
            branch = self.build_branch(taxid)  # jeweils Wurzel bis Blatt
            current_node_in_tree = root  # Beginne an der Wurzel
            # Addiere die Reads für die Wurzel
            current_node_in_tree.cumulative_reads += reads_for_current_taxid
            add_new_nodes_to_tree = False
            for node_in_branch in branch:  # Durchlaufe die Knoten des Zweiges
                if add_new_nodes_to_tree:
                    new_node = self.Node(node_in_branch.name, node_in_branch.taxid, node_in_branch.rank,
                                         current_node_in_tree, reads_for_current_taxid)
                    current_node_in_tree = current_node_in_tree.add_child(
                        new_node)
                else:
                    child = current_node_in_tree.get_child(
                        node_in_branch.taxid)  # Prüft, ob nächster Knoten des Zweiges bereits im Baum ist
                    if child:
                        # Addiere die Reads des Zweiges zu bestehendem Knoten
                        child.cumulative_reads += reads_for_current_taxid
                        current_node_in_tree = child
                    else:
                        new_node = self.Node(node_in_branch.name, node_in_branch.taxid, node_in_branch.rank,
                                             current_node_in_tree, reads_for_current_taxid)
                        current_node_in_tree = current_node_in_tree.add_child(
                            new_node)
                        add_new_nodes_to_tree = True
        return root

    def write_data_for_nodes_in_branch(self, file, node, accession_counts_by_taxid, total_reads, level=0):
        indent = '  ' * level
        reads_per_taxid = accession_counts_by_taxid.get(node.taxid, 0)
        percentage = self.calculate_percentage_of_reads(
            node.cumulative_reads, total_reads)
        file.write(
            f"{percentage}\t{node.cumulative_reads}\t{reads_per_taxid}\t{node.rank}\t{node.taxid}\t{indent}{node.name}\n")
        for child in node.children:
            self.write_data_for_nodes_in_branch(
                file, child, accession_counts_by_taxid, total_reads, level + 1)

    def create_output_file(self, tree, accession_counts_by_taxid, unclassified_reads, percentage_of_unclassified_reads,
                           total_reads, output_filename):
        with open(output_filename, 'w') as file:
            file.write(
                f"{percentage_of_unclassified_reads}\t{unclassified_reads}\t{unclassified_reads}\t{'U'}\t{'0'}\tunclassified\n")
            self.write_data_for_nodes_in_branch(
                file, tree, accession_counts_by_taxid, total_reads)


if __name__ == '__main__':
    pass
