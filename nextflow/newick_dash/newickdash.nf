nextflow.enable.dsl=2

params.input = 'results/converted_out/converted.report'

process newickToKraken {
  container params.python_plotly_container_path
  containerOptions "--bind ${projectDir}:${projectDir}"

      input:
      path input  

      output:
      path newick

      script:
      """
      python ${projectDir}/newick_dash/krakentonewick.py ${input} 
      mv newick.txt newick
      """
}

process toKraken{
container params.python_container_path
containerOptions "--bind ${projectDir}:${projectDir}"

    input:
      path input
    output:
      path "${input.getSimpleName()}_converted.kraken"
    script:
    """
    export PYTHONPATH=\$PYTHONPATH:${projectDir}/newick_dash && python ${projectDir}/newick_dash/script/main.py ${input} ${projectDir}/newick_dash/Database/database.db > ${input.getSimpleName()}_converted.kraken
    """
}

process dashToTree{
container params.python_plotly_container_path
containerOptions "--bind ${projectDir}:${projectDir}"

    input:
      path input

    output:
      path plot
  
    script:
    """
    python ${projectDir}/newick_dash/Dash_app/dash_tree_nextto_heatmap.py ${input} > plot
    """
}
workflow{
 newickToKraken(params.input)
}

workflow visualize{
  take:
    input
  main:
    input.view()
    kraken = toKraken(input)
    output = dashToTree(kraken.collect())
  emit:
    output
}

