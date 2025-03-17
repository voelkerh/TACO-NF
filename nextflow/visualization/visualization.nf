nextflow.enable.dsl = 2

workflow visualize {
  take:
  tree_file
  kraken_reports

  main:
  tree_file.view()
  kraken_reports.view()
  START_DASH_APP(tree_file, kraken_reports)
}

/* 
  Input: txt file with joint tree representation in newick format + classification outputs & ground truth in kraken report format
  Output: Dash app with tree and heatmap
*/

process START_DASH_APP {
  container params.python_plotly_container_path
  containerOptions '--bind ${projectDir}:${projectDir}'

  input:
  path tree_file
  path kraken_reports

  script:
  """
  python ${projectDir}/visualization/dash_app/dash_app.py ${tree_file} ${kraken_reports.join(' ')}
  """
}
