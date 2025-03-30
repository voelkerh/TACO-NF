from to_kraken_converters.abstract_converter import AbstractConverter
from Database.taxdb import TaxDB


class GTConverter(AbstractConverter):

    def __init__(self, taxdb: TaxDB):
        self.taxdb = taxdb

    def can_convert(self, filename: str) -> bool:
        """
        Checks if the file is in a ground truth format.
        """
        with open(filename, 'r') as f:
            if f.readline().strip().split(",")[0] == "taxid":
                return True

    def convert(self, filename: str, output_filename: str) -> str:
        """
        Converts the ground truth file and creates an output format.
        """
        if not self.can_convert(filename):
            raise ValueError(
                f"The file {filename} cannot be converted. It isn't a ground truth file.")

        # Reading the file and extracting the data
        total_reads = self.count_numreads(filename)
        accession_counts_by_taxid = self.count_alignments_per_taxid_from_lines(
            filename)

        # Creating the tree
        tree = self.build_tree(accession_counts_by_taxid)

        # Writing the output file
        self.create_output_file(
            tree, accession_counts_by_taxid, total_reads, output_filename)

        return "Conversion successful (gt to kraken)."

    def count_numreads(self, input_file):
        numreads = 0
        with open(input_file, 'r') as infile:
            header = infile.readline().strip()
            for line in infile:
                try:
                    tax_id, read_number = line.strip().split(',')
                    numreads += int(read_number)
                except ValueError as e:
                    print(f"Error processing line: {line.strip()} - {e}")
                    continue
        return numreads

    def count_alignments_per_taxid_from_lines(self, input_file):
        accession_counts = {}

        with open(input_file, 'r') as f:
            header = f.readline().strip()

            for line in f:
                try:
                    tax_id, read_number = line.strip().split(',')
                    read_number = int(read_number)

                    if tax_id in accession_counts:
                        accession_counts[tax_id] += read_number
                    else:
                        accession_counts[tax_id] = read_number
                except ValueError as e:
                    print(f"Error processing line: {line.strip()} - {e}")
                    continue

        return accession_counts

    def calculate_percentage_of_reads(self, number_of_reads, total_reads):
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
        # print(taxid)
        while taxid and taxid != '1':  # Wurzel erreicht
            parent_taxid = self.get_parent_taxid_from_taxonomic_data(taxid)
            # print(parent_taxid)
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

    def build_tree(self, accession_counts_by_taxid):
        root = self.Node('root', 1, ' ', None, 0)
        for id in accession_counts_by_taxid:
            taxid = id
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
                    new_node = self.Node(node_in_branch.name, node_in_branch.taxid,
                                         node_in_branch.rank, current_node_in_tree, reads_for_current_taxid)
                    current_node_in_tree = current_node_in_tree.add_child(
                        new_node)
                else:
                    # Prüft, ob nächster Knoten des Zweiges bereits im Baum ist
                    child = current_node_in_tree.get_child(
                        node_in_branch.taxid)
                    if child:
                        # Addiere die Reads des Zweiges zu bestehendem Knoten
                        child.cumulative_reads += reads_for_current_taxid
                        current_node_in_tree = child
                    else:
                        new_node = self.Node(node_in_branch.name, node_in_branch.taxid,
                                             node_in_branch.rank, current_node_in_tree, reads_for_current_taxid)
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

    def create_output_file(self, tree, accession_counts_by_taxid, total_reads, output_filename):
        with open(output_filename, 'w') as file:
            file.write(
                # f"{percentage_of_unclassified_reads:<6}\t{unclassified_reads:<15}\t{unclassified_reads:<15}\t{'U':<4}\t{'0':<8}\tunclassified\n")
                f"{0.0}\t{0}\t{0}\t{'U'}\t{0}\tunclassified\n")
            self.write_data_for_nodes_in_branch(
                file, tree, accession_counts_by_taxid, total_reads)


if __name__ == '__main__':
    pass
