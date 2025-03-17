nextflow.enable.dsl = 2

/*
  Ablauf:
  1. Konvertiere Ground Truth in Kraken-Format
  2. Konvertiere alle Classification Outputs in Kraken-Format
  3. Konvertiere zusätzlich alle Kraken-Files in Newick-Format
  4. Führe Newick-Files mit merger zusammen
  5. Gebe übergreifenden Baum in Newick-Format und vollständigen Satz an Kraken-Files aus
*/

params.input = 'results/converted_out/converted.report'

workflow {
  inputChannel = Channel.fromPath(params.input)
  convert(inputChannel)
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
    kraken_files = krakenChannel
    newick_file = merged_tree
}

process INPUT_TO_KRAKEN {
  container params.python_container_path
  containerOptions '--bind ${projectDir}:${projectDir}'

  input:
    path input

  output:
    path '${input.getSimpleName()}_converted.kraken'

  script:
    """
    export PYTHONPATH=\$PYTHONPATH:${projectDir}/conversion && python ${projectDir}/conversion/to_kraken_converters/main.py ${input} ${projectDir}/conversion/database/database.db > ${input.getSimpleName()}_converted.kraken
    """
}

process KRAKEN_TO_NEWICK {
  container params.python_plotly_container_path
  containerOptions '--bind ${projectDir}:${projectDir}'

  input:
    path input

  output:
    path 'newick.txt'

  script:
    """
    python ${projectDir}/conversion/kraken_to_newick_converter/kraken_to_newick.py ${input}
    """
}

process MERGE_NEWICK {
  container params.python_plotly_container_path
  containerOptions '--bind ${projectDir}:${projectDir}'

  input:
  path newick_files

  output:
  path 'merged_tree.txt'

  script:
    """
    python ${projectDir}/conversion/newick_merger/newick_merger.py ${newick_files.join(' ')}
    """
}
