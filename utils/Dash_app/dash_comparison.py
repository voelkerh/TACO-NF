"""
This script compares the taxonomic classification results of different tools.
It is based on Dash and Plotly as well as the phylotree Plotly extension.

Usage:
python dash_comparison.py <newick_file> <kraken_file> <kraken_file> ...
Make sure that the newick file has "newick" in its name.

Current usage:
python dash_comparison.py sample_files/newick_kraken.txt sample_files/kraken.report
"""
import sys
import pandas as pd

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
from phylotree import create_phylogenetic_tree

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
        data.columns = [file_name, 'Phylo_Label']
        data.set_index('Phylo_Label', inplace=True)
        dfs[file] = data[file_name]
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

global_files = process_program_arguments()
global_dataframe = prepare_combined_dataframe(global_files)
global_max_indent = get_max_indent(global_dataframe)
global_newick_str = get_newick_string()
# rank_marks = {
#     0: "Root",
#     1: "Domain",
#     2: "Kingdom",
#     3: "Phylum",
#     4: "Class",
#     5: "Order",
#     6: "Family",
#     7: "Genus",
#     8: "Species"
# }

app = Dash(__name__)

app.layout = html.Div(
    children=[
        html.Header([
            html.H1('Comparison of Taxonomic Classification Tools for WGS Data'),
            html.Div(
                className='treeLevel',
                children=[
                    html.P("Taxonomic rank:"),
                    dcc.Slider(
                        id='hierarchy-level-slider',
                        min=0,
                        max=global_max_indent,
                        marks={i: f'{i}' for i in range(0, global_max_indent + 1, 2)},
                        # max=len(rank_marks)-1,
                        # marks=rank_marks,
                        value=0,
                        step=1,
                        className='slider'
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
    ],
)

@app.callback(
    [Output("tree", "figure")],
    [Input("hierarchy-level-slider", "value")]
)

def filter_figure(selected_level):
    """
    Filters by the selected level and returns the combinedfigure.
    """
    fig = update_tree(selected_level)

    df_level_filtered = filter_dataframe_by_level(global_dataframe, selected_level)
    fig_heatmap, heatmap_labels = update_heatmap(df_level_filtered)
    combined_figure = combine_figures(fig, fig_heatmap)
    combined_figure = update_layout(combined_figure, heatmap_labels)

    return [combined_figure]

def update_tree(selected_level):
    """
    Updates the phylogenetic tree.
    """
    fig_tree = create_phylogenetic_tree(global_newick_str, selected_level, show_labels=False)
    for i in range(len(fig_tree["data"])):
        fig_tree["data"][i]["xaxis"] = "x"
    return fig_tree

def filter_dataframe_by_level(df, level):
    """
    Filters the dataframe by the selected level.
    """
    levels = df.index.map(lambda x: (len(x) - len(x.lstrip(' '))) // 2)
    df_filter = []

    for idx, label in enumerate(df.index):
        if levels[idx] == level:
            df_filter.append(label)
            continue
        if idx < len(levels) - 1:
            if levels[idx] > levels[idx+1] and levels[idx] < level:
                df_filter.append(label)
                continue

    return df.loc[df_filter]

def update_heatmap(df_level_filtered):
    """
    Updates the heatmap.
    """
    heatmap_labels = format_labels(df_level_filtered.index)
    fig_heatmap = go.Heatmap(
        x=df_level_filtered.columns,
        y=heatmap_labels,
        z=df_level_filtered.values,
        colorscale='darkmint',
        text=df_level_filtered.values,
        texttemplate="%{text}",
        showscale=False,
        xaxis='x2',
    )
    return fig_heatmap, heatmap_labels

def format_labels(heatmap_labels):
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

    # Synchronisiert y-Achse der Heatmap mit der des Dendrogramms
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
    fig.update_layout(
        yaxis={
            'showticklabels': True,
            'ticktext': tick_labels,
            'ticks': '',
            'tickvals': list(range(len(tick_labels))),
            'position': 0.6,
            'side': 'left',
            'autorange': 'reversed',
            # 'fixedrange' : True
        },
    )
    return fig

# Run app
if __name__ == '__main__':
    app.run(debug=True)
