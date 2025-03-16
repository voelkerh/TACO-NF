nextflow.enable.dsl=2

/* 
  Input: txt file with joint tree representation in newick format + classification outputs & ground truth in kraken report format
  Output: Dash app with tree and heatmap
*/

process START_DASH_APP {
container params.python_plotly_container_path
containerOptions '--bind ${projectDir}:${projectDir}'

    input:
      path input

    output:
      path plot
  
    script:
    """
    python ${projectDir}/visualization/dash_app/dash_tree_nextto_heatmap.py ${input} > plot
    """
}

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

