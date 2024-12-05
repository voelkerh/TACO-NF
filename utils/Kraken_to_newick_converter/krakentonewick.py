import sys

"""
Script to convert Kraken output to Newick format.
Taken from: https://github.com/sridhar0605/kraken-review (MIT License)
"""
import csv
import re

from pathlib import Path

import ete3

__all__ = [
    'KrakenSummary']

INDENT_UNIT = 4 #vorher 2


class KrakenSummary(object):
    def __init__(self, infile, ignore_unclassified=False):
        self.infile = Path(infile).expanduser().resolve()
        self.ignore_unclassified = ignore_unclassified

        nodes = {}
        current_root_index = 0
        re_indent = re.compile('^\s*')

        tree = ete3.Tree()
        root = tree.add_child(name='root')

        nodes[current_root_index] = root

        with self.infile.open() as handle:
            for line in csv.reader(handle, delimiter='\t'):
                fraction, cumulative, count, order, tax_id, taxa_entry = line

                indent_size = len(re_indent.match(taxa_entry).group())
                taxa_name = re_indent.sub('', taxa_entry)

                if taxa_name == 'root':
                    continue

                if not ignore_unclassified and taxa_name == 'unclassified':
                    tree.add_child(name='unclassified')

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
        return self.tree.write(format=1) # Format 1 keeps the internal node names, manually added

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'"{self.infile}", '
            f'ignore_unclassified={self.ignore_unclassified})')

"""
Additional code to convert Kraken output to Newick format in txt-file.
"""

def main():
    if len(sys.argv) < 2:
        print("Usage: python krakentonewick.py <infile> [--ignore-unclassified]")
        sys.exit(1)
    
    infile = sys.argv[1]
    ignore_unclassified = '--ignore-unclassified' in sys.argv

    kraken_summary = KrakenSummary(infile, ignore_unclassified)
    newick_string = kraken_summary.newick

    with open('newick.txt', 'w') as outfile:
        outfile.write(newick_string)
        print("Newick string written to newick.txt")

if __name__ == '__main__':
    main()
