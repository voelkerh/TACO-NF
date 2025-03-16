nextflow.enable.dsl = 2

params.input = 'results/converted_out/converted.report'

// process START_DASH_APP {
// container params.python_plotly_container_path
// containerOptions '--bind ${projectDir}:${projectDir}'

//     input:
//       path input

//     output:
//       path plot

//     script:
//     """
//     python ${projectDir}/visualization/dash_app/dash_tree_nextto_heatmap.py ${input} > plot
//     """
// }

workflow {
  KRAKEN_TO_NEWICK(params.input)
}

workflow visualize {
  take:
  input

  main:
  input.view()
  kraken = TO_KRAKEN(input)
  output = START_DASH_APP(kraken.collect())

  emit:
  output
}

process KRAKEN_TO_NEWICK {
  container params.python_plotly_container_path
  containerOptions '--bind ${projectDir}:${projectDir}'

  input:
  path input

  output:
  path newick

  script:
  """
    python ${projectDir}/conversion/kraken_to_newick_converter/krakentonewick.py ${input} 
    mv newick.txt newick
    """
}

process TO_KRAKEN {
  container params.python_container_path
  containerOptions '--bind ${projectDir}:${projectDir}'

  input:
  path input

  output:
  path '${input.getSimpleName()}_converted.kraken'

  script:
  """
  export PYTHONPATH=\$PYTHONPATH:${projectDir}/conversion && python ${projectDir}/conversion/script/main.py ${input} ${projectDir}/conversion/database/database.db > ${input.getSimpleName()}_converted.kraken
  """
}
