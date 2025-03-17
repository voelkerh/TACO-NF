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
    python ${projectDir}/conversion/kraken_to_newick_converter/kraken_to_newick.py ${input} 
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
    export PYTHONPATH=\$PYTHONPATH:${projectDir}/conversion && python ${projectDir}/conversion/to_kraken_converters/main.py ${input} ${projectDir}/conversion/database/database.db > ${input.getSimpleName()}_converted.kraken
    """
}
