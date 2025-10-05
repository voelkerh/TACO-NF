"""
This script creates a Dash app to compare the taxonomic classification results
of different taxonomic classification tools.
It is based on Dash and Plotly as well as the phylotree Plotly extension.

Usage:
python dash_app.py <newick_file> <kraken_file> <kraken_file> ...
Make sure that the newick file has "newick" in its name.
"""
import sys
import re
import pandas as pd
from io import StringIO
from copy import deepcopy

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State
import plotly.graph_objects as go
from phylotree import create_phylogenetic_tree
from Bio import Phylo


def get_newick_string():
    """
    Reads the newick file and returns the newick string.
    """
    newick_path = sys.argv[1]
    newick_str = ''
    with open(newick_path, 'r', encoding='utf-8') as file:
        newick_str = file.read()
    return newick_str


def process_program_arguments():
    """
    Processes the program arguments and returns the kraken files.
    """
    kraken_files = []
    for arg in sys.argv[1:]:
        if 'newick' not in arg:
            kraken_files.append(arg)
    return kraken_files


def prepare_combined_dataframe(files):
    """
    Reads the kraken files and returns a combined dataframe.
    """
    dfs = {}
    for file in files:
        data = pd.read_csv(file, sep='\t', header=None, usecols=[0, 5])
        file_name = file.split('/')[-1]
        file_name = re.sub(
            r'_(converted|aligned)|(merged|cleaned)_|.kraken', '', file_name)
        data.columns = [file_name, 'Phylo_Label']
        data.set_index('Phylo_Label', inplace=True)
        dfs[file_name] = data[file_name]
    combined_df = pd.concat(dfs.values(), axis=1, keys=dfs.keys(), sort=False)
    return combined_df.fillna(0)


def get_max_indent(combined_df):
    """
    Calculates the maximum indent of the labels in the combined dataframe.
    """
    max_indent = 0
    for label in combined_df.index:
        indent = (len(label) - len(label.lstrip('  '))) // 2
        max_indent = max(max_indent, indent)
    return max_indent


global_newick_str = get_newick_string()
global_files = process_program_arguments()
global_dataframe = prepare_combined_dataframe(global_files)
global_max_indent = get_max_indent(global_dataframe)
global_phylo_tree = Phylo.read(StringIO(global_newick_str), "newick")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    children=[
        html.Header([
            dbc.Button("i", id="open", n_clicks=0),
            html.Div(
                className='mainHeader',
                children=[
                    html.H1(
                        'Comparison of Taxonomic Classification Tools for WGS Data'),
                    html.Div(
                        className='treeLevel',
                        children=[
                            html.P("Tree level:"),
                            dcc.Slider(
                                id='hierarchy-level-slider',
                                min=0,
                                max=global_max_indent,
                                marks={i: f'{i}' for i in range(
                                    0, global_max_indent + 1, 2)},
                                value=0,
                                step=1,
                                className='slider'
                            ),
                        ]
                    )
                ]
            )
        ]),
        html.Div(
            className='content-wrapper',
            children=[
                dcc.Graph(id="tree"),
            ],
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Important")),
                dbc.ModalBody(
                    "This visualization requires running the nextflow pipeline in the background."),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close",
                               className="ms-auto", n_clicks=0)
                ),
            ],
            id="modal",
            is_open=True,
        ),
    ],
)


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    """
    Helper function to toggle information on pipline required running in the background.
    """
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    [Output("tree", "figure")],
    [Input("hierarchy-level-slider", "value")]
)
def filter_figure(selected_level):
    """
    Filters by the selected level and returns the combinedfigure.
    """
    fig = update_tree(selected_level)

    df_level_filtered = filter_dataframe_by_current_leaves(
        global_dataframe, selected_level)
    fig_heatmap, heatmap_labels = update_heatmap(df_level_filtered)
    combined_figure = combine_figures(fig, fig_heatmap)
    combined_figure = update_layout(combined_figure, heatmap_labels)

    return [combined_figure]


def update_tree(selected_level):
    """
    Updates the phylogenetic tree.
    """
    fig_tree = create_phylogenetic_tree(
        global_newick_str, selected_level, show_labels=False)
    for i in range(len(fig_tree["data"])):
        fig_tree["data"][i]["xaxis"] = "x"
    return fig_tree


def filter_dataframe_by_current_leaves(df, selected_level):
    """
    Filter mechanism based on leaves of current tree level.
    Ensures congruent heatmap index and phylotree leaves.
    """
    leaves_order = get_leaves_from_tree(selected_level)
    df_norm = df.copy()
    df_norm.index = df_norm.index.map(normalize_string)
    df_norm = df_norm[~df_norm.index.duplicated(keep='first')]
    present = [leaf for leaf in leaves_order if leaf in df_norm.index]

    return df_norm.loc[present]


def normalize_string(s: str) -> str:
    """
    Ensure strings in index and leaves have same format.
    Required to make dataframe filter by leaves upon level selection stable.
    """
    s = s.strip().lower()
    s = re.sub(r'[\[\]\(\)]', '_', s)
    s = re.sub(r'\b(str|subsp|serovar|variant)\._', r'\1_', s)
    s = re.sub(r'[^0-9a-z]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s


def get_leaves_from_tree(level):
    """
    Trim tree to selected level and extract leaves in current order.
    Extracted leaves serve as a basis to filter heatmap by level. 
    """
    try:
        tree_trimmed = deepcopy(global_phylo_tree)
        tree_trimmed.root = _set_root_node(tree_trimmed)
        unclassified = _cut_unclassified_clade(tree_trimmed)

        if level == 0:
            candidates = [tree_trimmed.root]
            if unclassified is not None:
                candidates.append(unclassified)
            return [normalize_string(c.name) for c in candidates if c.name]

        _trim_tree_to_display_level(tree_trimmed.root, 0, level)
        leaves = tree_trimmed.get_terminals()
        names = [normalize_string(
            leaf.name) for leaf in leaves if leaf.name]
        return names
    except Exception as e:
        raise ValueError(f"Invalid Newick format: {e}") from e


def _set_root_node(tree):
    for clade in tree.find_clades(order="level"):
        if clade.name == "root":
            tree.root = clade
            break
    else:
        tree.root.name = tree.root.name or "root"
    return tree.root


def _cut_unclassified_clade(tree):
    for clade in tree.root.clades:
        if normalize_string(clade.name) == "unclassified":
            unclassified = clade
            tree.root.clades.remove(unclassified)
            tree.root.clades.extend(unclassified.clades)
            unclassified.clades = []
            return unclassified
    return None


def _trim_tree_to_display_level(clade, current_level, display_level):
    if current_level >= display_level:
        clade.clades = []
    else:
        for child in clade.clades:
            _trim_tree_to_display_level(
                child, current_level + 1, display_level)


def update_heatmap(df_level_filtered):
    """
    Update heatmap based on level filtered dataframe upon selection of tree level.
    """
    heatmap_labels = format_labels(df_level_filtered.index)
    fig_heatmap = go.Heatmap(
        x=[str(column).split('/')[-1] for column in df_level_filtered.columns],
        y=heatmap_labels,
        z=df_level_filtered.values,
        colorscale='teal',
        text=df_level_filtered.values,
        texttemplate="%{text}",
        showscale=False,
        xaxis='x2',
    )
    return fig_heatmap, heatmap_labels


def format_labels(heatmap_labels):
    """
    Adds dashes for shorter labels to better visually connect to phylo tree leaves.
    """
    stripped_labels = [label.strip() for label in heatmap_labels]
    max_label_length = max(len(label) for label in stripped_labels)
    formatted_labels = []
    for label in stripped_labels:
        while len(label) < max_label_length:
            label = '-'+label
        formatted_labels.append(label)
    return formatted_labels


def combine_figures(fig_tree, fig_heatmap):
    """
    Combines the phylogenetic tree and the heatmap to one figure.
    """
    fig_tree.add_trace(fig_heatmap)

    # Synchronizes y-axis of heatmap with y-axis of dendrogram
    fig_tree.data[-1].y = fig_tree.layout.yaxis.tickvals

    return fig_tree


def update_layout(fig, tick_labels):
    """
    Updates the layout of the combined figure.
    """
    # Overall layout
    fig.update_layout(
        {
            'showlegend': False,
            'hovermode': 'closest',
            'plot_bgcolor': 'white',
            'font': {
                'family': 'Anonymous Pro, monospace'
            }
        }
    )

    # x-axes
    fig.update_layout(
        xaxis={
            'domain': [0, 0.6],  # Tree area - 50%
            'showticklabels': False,
        },
        xaxis2={
            'domain': [0.6, 1],  # Heatmap area - 50%
            'side': 'top',
            'ticktext': global_dataframe.columns,
            'showticklabels': True,
            'ticks': '',
        }
    )

    # y-axes
    visible_rows = 10
    fig.update_layout(
        yaxis={
            'showticklabels': True,
            'ticktext': tick_labels,
            'ticks': '',
            'tickvals': list(range(len(tick_labels))),
            'position': 0.6,
            'side': 'left',
            'range': [visible_rows - 0.5, -0.5]
        },
    )
    return fig


# Run app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
