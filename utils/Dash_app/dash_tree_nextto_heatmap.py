import sys
import numpy as np 
import pandas as pd 

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
from phylotree import create_phylogenetic_tree

def get_newick_string():
    newick_path = sys.argv[1]
    newick_str = ''
    with open(newick_path, 'r') as file:
        newick_str = file.read()
    return newick_str

def process_program_arguments():
    kraken_files = []
    for arg in sys.argv[1:]:
        if 'newick' not in arg:
            kraken_files.append(arg)
    return kraken_files

def get_file_names(file_paths):
    return [{'label': file.split('/')[-1], 'value': file} for file in file_paths]

def prepare_combined_dataframe(files):
    dfs = {}
    for file in files:
        data = pd.read_csv(file, sep='\t', header=None, usecols=[0, 5])
        data.columns = [f'{file}', 'Phylo_Label']
        data.set_index('Phylo_Label', inplace=True)
        dfs[file] = data[f'{file}']
    combined_df = pd.concat(dfs.values(), axis=1, keys=dfs.keys(), sort=False)
    return combined_df.fillna(0)

def get_max_indent(combined_df):
    max_indent = 0
    for label in combined_df.index:
        indent = (len(label) - len(label.lstrip('  '))) // 2
        if indent > max_indent:
            max_indent = indent
    return max_indent

def filter_dataframe_by_level(df, level):
    if level == None:
        return filter_dataframe_all_leaves(df)
    df_filtered = df[df.index.map(lambda x: (len(x) - len(x.lstrip(' '))) // 2 == level)]
    return df_filtered

def filter_dataframe_all_leaves(df):
    labels = df.index
    leaf_indices = []
    for i in range(len(labels)):
        current_indent = (len(labels[i]) - len(labels[i].lstrip(' '))) // 2
        if i == len(labels) - 1: # last element always leaf
            leaf_indices.append(i)
        else:
            next_indent = (len(labels[i+1]) - len(labels[i+1].lstrip(' '))) // 2
            if next_indent <= current_indent:
                leaf_indices.append(i)
    df_filtered = df.iloc[leaf_indices]
    return df_filtered

files = process_program_arguments()
file_names = get_file_names(files)
dataframe = prepare_combined_dataframe(files)
newick_str = get_newick_string()

app = Dash(__name__)

app.layout = html.Div(
        children=[
            html.Header(
                children=[
                    html.Div(
                        html.H1('Comparison of Taxonomic Classification Tools for WGS Data'),
                    ),
                    html.Nav(
                        children=[
                            html.Div(
                                className='treeLevel',
                                children=[
                                    html.P("Tree level:"),
                                    dcc.Slider(
                                            id='hierarchy-level-slider',
                                            min=0,
                                            max=get_max_indent(dataframe),
                                            marks={i: f'{i}' for i in range(0, get_max_indent(dataframe) + 1, 2)},
                                            value=0,
                                            step=1,
                                            className='slider'
                                    ),
                                    dcc.Checklist(
                                            id='show-all-levels',
                                            options=[{'label': 'All leaves', 'value': 'all'}],
                                            value=[],
                                    )
                                ]
                            ),

                            html.Div(
                                className='filesIncluded',
                                children=[
                                    html.P("Files included:"),
                                    dcc.Checklist(
                                        id='files',
                                        options=file_names,
                                        value=[file['value'] for file in file_names] if file_names else [],
                                        labelClassName='checklist'
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className='content-wrapper',
                children=[
                    dcc.Graph(id="tree"),
                    dcc.Graph(id="graph"),
                ],
            ),
            html.Footer(
                children=[
                    html.Span(
                        className='footer-text',
                        children=[
                            html.P('Projektstudium: Analyse von Genomsequenzierungsdaten zur Diagnostik von Infektionskrankheiten'),
                            html.P('Wintersemester 2024/25'),
                        ],
                    ),
                    html.Img(
                        className='footer-logo',
                        src='https://upload.wikimedia.org/wikipedia/commons/7/7e/Logo_HTW_Berlin.svg',
                    ),
                ],
            )
        ],
    )

@app.callback(
    [Output("graph", "figure"), Output("tree", "figure")],
    [Input("files", "value"), Input("hierarchy-level-slider", "value"), Input("show-all-levels", "value")]
)

def filter_tree_heatmap(selected_files, selected_level, show_all):
    
    fig_tree = update_tree(selected_level, show_all)
    
    if not selected_files:
        return update_empty_heatmap(), fig_tree

    combined_df = prepare_combined_dataframe(selected_files)
    df_level_filtered = filter_dataframe_by_level(combined_df, None if show_all else selected_level)
    fig_heatmap = update_heatmap(df_level_filtered)

    return fig_heatmap, fig_tree

def update_tree(selected_level, show_all):
    if show_all:
        fig_tree = create_phylogenetic_tree(newick_str)
    else:
        fig_tree = create_phylogenetic_tree(newick_str, selected_level)
    
    fig_tree.update_layout({
        'title': 'Taxonomic Information',
        'title_x': 0.5,
        'plot_bgcolor': 'white',
        'yaxis': {
            'showticklabels': False,
        }
    })
    return fig_tree

def update_empty_heatmap():
    fig_heatmap = go.Figure()
    fig_heatmap.add_annotation(
        x=0.5,
        y=0.5,
        text="No files selected",
        xref="paper",
        yref="paper",
        showarrow=False
    )
    fig_heatmap.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor = 'white'
    )
    return fig_heatmap

def update_heatmap(df_level_filtered):
    num_rows = df_level_filtered.shape[0]
    fig_height = max(800, num_rows * 40)    
    clades_labels = df_level_filtered.index
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=df_level_filtered.values,
        x=df_level_filtered.columns,
        y=clades_labels,
        colorscale='darkmint',
        text=df_level_filtered.values,
        texttemplate="%{text}",
        showscale=False
    ))
    
    fig_heatmap.update_layout(
        title_text='Classification Results',
        title_x=0.5,
        height=fig_height,
        yaxis=dict(
            ticktext=clades_labels,
            autorange='reversed',
            side='right'
        ),
        xaxis=dict(
            ticktext=df_level_filtered.columns,
            side='top'
        )
    )
    return fig_heatmap

# Run app
if __name__ == '__main__':
    app.run(debug=True)