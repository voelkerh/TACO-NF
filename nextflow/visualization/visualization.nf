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

process START_DASH_APP {
  container file(params.python_plotly_container_path)
  containerOptions '--bind ${projectDir}:${projectDir}'

  input:
  path tree_file
  path kraken_reports

  script:
  """
  echo "Dash App: http://127.0.01:8050"
  python3 ${projectDir}/visualization/Dash_app/dash_app.py ${tree_file} ${kraken_reports.join(' ')}
  """
}
