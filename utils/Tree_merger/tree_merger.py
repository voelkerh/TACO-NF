# Description: Merges two or more Newick strings (trees) into one Newick string without distance values
# Input: Two or more Newick strings as .txt files
# Output: .txt files with 1 Newick string without distance values
# Use: after conversion to kraken-formats, before visualization in Dash

import sys
import re
from io import StringIO
from Bio import Phylo
from copy import deepcopy

def process_program_arguments():
    tree_files = []
    if len(sys.argv) < 2:
        print('Please provide at least two files as arguments.')
        sys.exit(1)
    for arg in sys.argv[1:]:
        tree_files.append(arg)
    return tree_files

def get_tree_from_file(file):
    newick = ''
    with open(file, 'r') as file:
        newick = file.read()
    newick_str = newick.replace(" ", "_")
    handle = StringIO(newick_str)
    return Phylo.read(handle, "newick")

def merge_two_trees(base_tree, additional_tree):
    merged_tree = deepcopy(base_tree)
    merge_clades(merged_tree.root, additional_tree.root)    
    return merged_tree

def merge_clades(base_clade, additional_clade):
    reference_clades = {clade.name: clade for clade in base_clade.clades}
    if reference_clades:
        for additional_child in additional_clade.clades:
            if additional_child.name not in reference_clades:
                base_clade.clades.append(deepcopy(additional_child))
                continue
            else:
                base_child = reference_clades[additional_child.name]
                merge_clades(base_child, additional_child)

def merge_trees(trees):
    merged_tree = trees[0]
    for tree in trees[1:]:
        merged_tree = merge_two_trees(merged_tree, tree)
    return merged_tree

def tree_to_newick_no_distance(tree):
    output = StringIO()
    Phylo.write(tree, output, 'newick')
    newick = output.getvalue()
    output.close()
    newick_no_distance = re.sub(r':\d+(\.\d+)?', '', newick)
    return newick_no_distance

def write_newick_to_output_file(newick_str):
    with open('merged_tree.txt', 'w') as file:
        file.write(newick_str)

tree_files = process_program_arguments()
trees = [get_tree_from_file(file) for file in tree_files]
merged_tree = merge_trees(trees)
newick_no_distance = tree_to_newick_no_distance(merged_tree)
write_newick_to_output_file(newick_no_distance)