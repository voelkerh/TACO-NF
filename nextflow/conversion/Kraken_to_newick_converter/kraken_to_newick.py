"""
Script converts kraken2 report format to tree representation in Newick format.
The result will be saved as .txt file.
Built on: https://github.com/sridhar0605/kraken-review (MIT License)
Note: set ignore_unclassified to True in pipeline.
"""

import sys
import csv
import re
from pathlib import Path

import ete3

__all__ = ['KrakenSummary']

INDENT_UNIT = 2  # Number of spaces in the indentation


class KrakenSummary(object):
    """
    Creates tree representation in Newick format upon instantiation.
    """

    def __init__(self, infile, ignore_unclassified=False):
        self.infile = Path(infile).expanduser().resolve()
        self.ignore_unclassified = ignore_unclassified

        nodes = {}
        current_root_index = 0
        re_indent = re.compile(r'^\s*')

        tree = ete3.Tree()
        root = tree.add_child(name='root')

        nodes[current_root_index] = root

        with self.infile.open(encoding="UTF-8") as handle:
            for line in csv.reader(handle, delimiter='\t'):
                _, _, _, _, _, taxa_entry = line

                indent_size = len(re_indent.match(taxa_entry).group())
                taxa_name = re_indent.sub('', taxa_entry)
                # Substitute characters which produce errors in Newick format
                taxa_name = re.sub(r"[():;,']", "_", taxa_name)

                if taxa_name == 'root':
                    continue

                if ignore_unclassified and taxa_name == 'unclassified':
                    continue

                if indent_size >= current_root_index:
                    parent = nodes[current_root_index]
                else:
                    parent = nodes[indent_size - INDENT_UNIT]

                child = parent.add_child(name=taxa_name)
                current_root_index = indent_size
                nodes[current_root_index] = child

        self.tree = tree

    @property
    def newick(self):
        """
        Writes tree representation from ete3.Tree object for external use.
        """
        # Format 1 keeps the internal node names, manually added
        return self.tree.write(format=1)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'"{self.infile}", '
            f'ignore_unclassified={self.ignore_unclassified})')


def main():
    """
    Wrapper to convert kraken2 report format to Newick format in txt-file.
    """

    if len(sys.argv) < 2:
        print(
            "Usage: python kraken_to_newick.py <infile> [--ignore-unclassified]")
        sys.exit(1)

    infile = sys.argv[1]
    ignore_unclassified = '--ignore-unclassified' in sys.argv

    kraken_summary = KrakenSummary(infile, ignore_unclassified)
    newick_string = kraken_summary.newick

    output_file = sys.argv[2]

    with open(output_file, 'w', encoding="UTF-8") as file:
        file.write(newick_string)


if __name__ == '__main__':
    main()
