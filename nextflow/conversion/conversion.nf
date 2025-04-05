nextflow.enable.dsl = 2

params.outdir = 'output/conversion'
params.conversion_workflow_store_dir = launchDir + 'store/6_conversion/'


process INPUT_TO_KRAKEN {
  container file(params.python_container_path)
  containerOptions '--bind ${projectDir}:${projectDir}'
  storeDir params.conversion_workflow_store_dir + '/input_converted_to_kraken/'
  publishDir params.outdir + '/kraken_files/', mode:'copy'

  input:
    path input

  output:
    path "${input.getSimpleName()}_converted.kraken"

  script:
    """
    export PYTHONPATH=\${PYTHONPATH:-}:${projectDir}/conversion
    python3 ${projectDir}/conversion/to_kraken_converters/main.py ${input} ${projectDir}/conversion/Database/database.db ${input.getSimpleName()}_converted.kraken
    """
}

process KRAKEN_TO_NEWICK {
  container file(params.python_plotly_container_path)
  containerOptions '--bind ${projectDir}:${projectDir}'
  storeDir params.conversion_workflow_store_dir + '/kraken_to_newick/'

  input:
    path input

  output:
    path "${input.getSimpleName()}_newick.txt"

  script:
    """
    python3 ${projectDir}/conversion/Kraken_to_newick_converter/kraken_to_newick.py ${input} "${input.getSimpleName()}_newick.txt"
    """
}

process MERGE_NEWICK {
  container file(params.python_plotly_container_path)
  containerOptions '--bind ${projectDir}:${projectDir}'
  storeDir params.conversion_workflow_store_dir + '/merge_newick/'
  publishDir params.outdir + '/merged_newick/', mode:'copy'

  input:
  path newick_files

  output:
  path 'merged_newick_tree.txt'

  script:
    """
    python3 ${projectDir}/conversion/newick_merger/newick_merger.py ${newick_files.join(' ')}
    """
}

workflow convert {
  take:
    inputChannel

  main:
    inputChannel.view()

    krakenChannel = INPUT_TO_KRAKEN(inputChannel)
    newickChannel = KRAKEN_TO_NEWICK(krakenChannel)
    merged_tree = MERGE_NEWICK(newickChannel.collect())

  emit:
    kraken_files = krakenChannel.collect()
    newick_file = merged_tree
}
