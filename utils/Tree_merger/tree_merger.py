# Takes n Newick strings and merges them into a single tree
# input and output are .txt files
# Newick strings may not contain distance values

import sys
from io import StringIO
from Bio import Phylo

def process_program_arguments():
    tree_files = []
    for arg in sys.argv[1:]:
        tree_files.append(arg)
    return tree_files

def get_tree_from_file(file):
    return Phylo.read(file, 'newick')

def merge_two_trees(base_tree, additional_tree):
    return base_tree + additional_tree

def merge_trees(trees):
    merged_tree = trees[0]
    for tree in range(1, len(trees)):
        merged_tree = merge_two_trees(merged_tree, trees[tree])
    return merged_tree

def write_tree_to_output_file(tree):
    output = StringIO()
    Phylo.write(tree, output, 'newick')
    with open('merged_tree.txt', 'w') as file:
        file.write(output.getvalue())

tree_files = process_program_arguments()
trees = [get_tree_from_file(file) for file in tree_files]
merged_tree = merge_trees(trees)
write_tree_to_output_file(merged_tree)