nextflow.enable.dsl = 2

// Start Dash App on localhost based on merged tree in Newick format and classification results in kraken2 report format
process START_DASH_APP {
  container file(params.python_plotly_container_path)
  containerOptions '--bind ${projectDir}:${projectDir}'

  input:
  path tree_file
  path kraken_reports

  script:
  """
  python3 ${projectDir}/visualization/Dash_app/dash_app.py ${tree_file} ${kraken_reports.join(' ')}
  """
}

workflow visualize {
  take:
    tree_file
    kraken_reports

  main:
    println("Dash App: http://127.0.01:8050")
    START_DASH_APP(tree_file, kraken_reports)
}
