nextflow.enable.dsl=2

params.input = 'results/converted_out/converted.report'
 
process newickToKraken {
  container params.python_container_path
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

process samToKraken{
container params.python_container_path

    input:
      path Bowtie2
    output:
      path KrakenBowtie2
    script:
    """
    python ${projectDir}/newick_dash/samtokrakentree.py ${Bowtie2} 2100000 ${baseDir}/database.db
    mv samtokraken.txt KrakenBowtie2
    """
}

process dashToTree{
container params.python_container_path
    input:
      path Kraken2
      path Bowtie2
      //path GTNewick
//path inputfiles

    output:
      path plot
  
    script:
//$inputfiles expands to " " separated list of files
    """
    python ${projectDir}/newick_dash/dash_tree_nextto_heatmap.py ${Kraken2} ${Bowtie2} > plot
    """
}
workflow{
 newickToKraken(params.input)
}

workflow visualize{
  take:
    Kraken2
    Bowtie2
    //input
  main:
    //input_file = file(params.input)
    //newick_output = newickToKraken(input)

//convert all files here using new converter interface

    samToKraken_out = samToKraken(Bowtie2)
    //output = dashToTree(Kraken2, samToKraken_out , newick_output)
    output = dashToTree(Kraken2, samToKraken_out )
//output = dashToTree(converted.collect()) <- this will be used to handle multiple inputs without explicit declaration
  emit:
    output
}

