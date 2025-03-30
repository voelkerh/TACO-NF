from to_kraken_converters.abstract_converter import AbstractConverter
from Database.taxdb import TaxDB


class KrakenConverter(AbstractConverter):

    def __init__(self, taxdb: TaxDB):
        self.taxdb = taxdb

    def can_convert(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                columns = line.strip().split('\t')
                if len(columns) >= 6 and (columns[5] == "root" or columns[5] == "unclassified"):
                    return True
        return False

    def convert(self, filename: str, output_filename: str) -> str:
        if not self.can_convert(filename):
            raise ValueError(
                f"The file {filename} cannot be converted. It is not a kraken file.")

        with open(filename, 'r') as infile:
            lines = infile.readlines()

        for i in range(2, len(lines)):
            try:
                line = lines[i]
                parts = line.split('\t')
                perc_reads, read_number, reads, rank, tax_id, name = parts[:6]

                tax_id = tax_id.strip()
                name = name.strip()

                indent = len(parts[5]) - len(parts[5].lstrip())

                # Check, if given name equals name from internal database; ensures consistency.
                updated_name = self.get_name_from_taxonomic_data(tax_id)
                if updated_name != name:
                    name = updated_name

                lines[i] = f"{perc_reads}\t{read_number}\t{reads}\t{rank}\t{tax_id}\t{' ' * indent}{name}\n"

            except ValueError as e:
                print(f"Error processing line: {line.strip()} - {e}")
                continue

        self.create_output_file(lines, output_filename)

        return "Conversion successful (kraken to kraken)."

    def create_output_file(self, lines, output_filename):
        with open(output_filename, 'w') as file:
            for line in lines:
                file.write(line)

    def get_name_from_taxonomic_data(self, taxid):
        return self.taxdb.get_name_from_taxonomic_data(taxid)


if __name__ == '__main__':
    pass
