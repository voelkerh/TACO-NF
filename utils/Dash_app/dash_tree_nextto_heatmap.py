from dash import Dash, dcc, html, Input, Output
import numpy as np 
import pandas as pd 

from pathlib import Path
import sys

path_root = Path(__file__).parents[0]
sys.path = [str(path_root) + '/local_plotly/packages/python/plotly/'] + sys.path

import plotly.graph_objects as go
import plotly.figure_factory as ff

import sys

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
                            html.P('Sommersemester 2024'),
                            html.P('Billy Andersson, Benjamin Riedl, Henriette Voelker')
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
    
    # Update Tree
    if show_all:
        display_level = np.inf
    else:
        display_level = selected_level
    fig_tree = ff.create_phylogenetic_tree(newick_str, display_level)

    fig_tree.update_layout({
        'title': 'Taxonomic Information',
        'title_x': 0.5,
        'showlegend':False, 
        'hovermode': 'closest',
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'xaxis': {
            'showticklabels': False,
            'showgrid': False,
            'zeroline': False,
            'automargin': True,
        },
        'yaxis': {
            'showticklabels': False,
            'showgrid': False,
            'zeroline': False,
            'automargin': True,
        }
    })

    # Update Heatmap
    if not selected_files:
        fig = go.Figure()
        fig.add_annotation(
            x=0.5,
            y=0.5,
            text="No files selected",
            showarrow=False,
            font=dict(size=20),
            xref="paper",
            yref="paper",
            xanchor="center",
            yanchor="middle"
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig, fig_tree

    combined_df = prepare_combined_dataframe(selected_files)
    if not combined_df.empty:
        # Filtere die Daten nach dem ausgewählten Level
        if show_all:
            df_level_filtered = filter_dataframe_all_leaves(combined_df)
            num_rows = combined_df.shape[0]
            fig_height = max(800, num_rows * 20)
        else:
            df_level_filtered = filter_dataframe_by_level(combined_df, selected_level)
            num_rows = df_level_filtered.shape[0]
            fig_height = max(800, num_rows * 40)
        
        clades_labels = df_level_filtered.index
        clades_labels = clades_labels[::-1]

        # Erstelle die Heatmap für den gefilterten DataFrame
        fig = go.Figure(data=go.Heatmap(
            z=df_level_filtered.values,
            x=df_level_filtered.columns,
            y=[label for label in clades_labels][::-1],
            colorscale='darkmint',
            text=df_level_filtered.values,
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title_text='Classification Results',
            title_x=0.5,
            height=fig_height,
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(num_rows)),
                ticktext=[str(label) for label in clades_labels][::-1],
                tickfont=dict(size=10),
                autorange='reversed'
            ),
            xaxis=dict(
                tickmode='array',
                tickvals=list(df_level_filtered.columns),
                ticktext=list(df_level_filtered.columns),
                tickfont=dict(size=10),
                side='top'
            )
        )
        fig_tree.update_layout(height=fig_height) 
        return fig, fig_tree

# Run app
if __name__ == '__main__':
    app.run(debug=True)