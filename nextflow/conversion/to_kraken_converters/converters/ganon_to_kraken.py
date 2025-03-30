from to_kraken_converters.abstract_converter import AbstractConverter
from Database.taxdb import TaxDB
from bigtree import dict_to_tree

class GanonConverter(AbstractConverter):

    def __init__(self, taxdb: TaxDB):
        self.taxdb = taxdb

    def can_convert(self, filename: str) -> bool:
        with open(filename, 'r') as f:
            header = f.readline().strip
            try:
                root = f.readline().strip().split("\t")[0]
                if root == "root":
                    return True
            except:
                return False

    def convert(self, filename: str, output_filename: str) -> str:
        if not self.can_convert(filename):
            raise ValueError(f"The file {filename} cannot be converted.It isn't a ganon file.")

        with open(filename, 'r') as infile:
            header = infile.readline().strip()
            unclassified, perc_unc = header.split()[-2:]
            perc_unc = round(float(perc_unc), 2)
            dct = {}
            for line in infile:
                try:
                    # columns = re.split(r'\s{2,}', line.strip())
                    columns = line.split('\t')
                    perc_reads = round(float(columns[8].strip()), 2)
                    read_number = columns[7].strip()
                    reads = int(columns[4]) + int(columns[5])
                    rank = self.get_rank_code_from_full_rank(columns[0].strip())
                    tax_id = columns[1].strip()
                    name = "root" if self.get_name_from_taxonomic_data(
                        tax_id) == 'all' else self.get_name_from_taxonomic_data(tax_id)
                    key = columns[2].replace("|", "/").strip()
                    dct[key] = {'line': [perc_reads, read_number, reads, rank, tax_id, name]}
                except ValueError as e:
                    print(f"Error processing line: {line.strip()} - {e}")
                    continue

        tree = dict_to_tree(dct)

        self.create_output_file(tree, perc_unc, unclassified, output_filename)

        return "Conversion successful. Output created in 'results/ganon.report'."

    def load_names_from_taxonomic_data(self, taxid):
        return self.taxdb.load_names_from_taxonomic_data(taxid)

    def load_full_ranks_from_taxonomic_data(self, rank):
        return self.taxdb.load_full_ranks_from_taxonomic_data(rank)

    def get_name_from_taxonomic_data(self, taxid):
        return self.taxdb.get_name_from_taxonomic_data(taxid)

    def get_full_rank_from_taxonomic_data(self, taxid):
        return self.taxdb.get_full_rank_from_taxonomic_data(taxid)

    def get_rank_code_from_full_rank(self, rank):
        return self.taxdb.get_rank_code_from_full_rank(rank)

    def write_data_for_nodes_in_branch(self, file, node, level=0):
        indent = '  ' * level
        file.write(
            f"{node.line[0]}\t{node.line[1]}\t{node.line[2]}\t{node.line[3]}\t{node.line[4]}\t{indent}{node.line[5]}\n")
        for child in node.children:
            self.write_data_for_nodes_in_branch(
                file, child, level + 1)

    def create_output_file(self, tree, percentage_of_unclassified_reads, unclassified_reads, output_filename):
        with open(output_filename, 'w') as file:
            file.write(
                f"{percentage_of_unclassified_reads}\t{unclassified_reads}\t{unclassified_reads}\t{'U'}\t{'0'}\tunclassified\n")
            self.write_data_for_nodes_in_branch(
                file, tree)


if __name__ == '__main__':
    pass
