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
      python ${projectDir}/visualization/krakentonewick.py ${input} 
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
    export PYTHONPATH=\$PYTHONPATH:${projectDir}/visualization && python ${projectDir}/visualization/script/main.py ${input} ${projectDir}/visualization/Database/database.db > ${input.getSimpleName()}_converted.kraken
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
    python ${projectDir}/visualization/Dash_app/dash_tree_nextto_heatmap.py ${input} > plot
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

