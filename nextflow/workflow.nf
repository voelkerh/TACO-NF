nextflow.enable.dsl = 2

include { process_sra_accessions } from './preparation/sra_accession_processing.nf'
include { quality_control_workflow } from './preparation/fastq_qc.nf'
include { kraken_classification } from './classification/kraken2/kraken2.nf'
include { bowtie_classification } from './classification/bowtie2/bowtie2.nf'
include { ganon_classification } from './classification/ganon2/ganon2.nf'
include { convert } from './conversion/conversion.nf'
include { visualize } from './visualization/visualization.nf'
// include { additional_tool_classification } from './classification/additional_tool/tool.nf'

workflow {
  
  if ( params.help ) {
    help = """\
    Comparison of taxonomic classification tools for WGS data
    ----------------------------------------------
    This pipeline runs a specified choice of classification tools (e.g., Kraken2, Bowtie2, Ganon2),
    converts their results into a unified format, and launches an interactive Dash app to explore results.

    Usage example:
      nextflow run main.nf --pipeline_input 'input/file.txt' --kraken2 --ganon2_db

    Required arguments:
      --input_file             Path to a .txt file listing SRA accessions and abundance of organisms
                               [default: ${params.input_file}]

    Optional classification tools (default: false):
      --kraken2                Enable Kraken2 classification.
      --bowtie2                Enable Bowtie2 alignment. Requires specification of refseq in input file, cf. README.
      --ganon2                 Enable Ganon classification.

    Tool-specific options:
      --kraken2_db             Name of the prebuilt Kraken2 database to download
                               [default: ${params.kraken2_db}]
      --ganon2_db              Ganon database groups to download (e.g. 'archaea', 'bacteria', ...)
                               [default: ${params.ganon2_db}]
      --ganon2_report_type     Report type for Ganon2 (e.g., 'abundance', 'reads', 'matches')
                               [default: ${params.ganon2_report_type}]

    Conversion options:
      --align_taxonomies       Attempt to align taxonomies between tools by inserting missing parent taxa
                               This may improve the allover consistency but can introduce new minor inconsistencies in the visualization.
                               [default: ${params.align_taxonomies}]

    Other:
      --help                   Show this help and exit
    
    """.stripIndent()

    println(help)
    exit(0)
  }

  user_input = Channel.fromPath(params.pipeline_input)

  // preparation
  fastq_and_groundtruth = process_sra_accessions(user_input)
  fastp_output = quality_control_workflow(fastq_and_groundtruth.fastq)

  // classification
  tools_output = Channel.of()

  if ( params.kraken2 ) {
    kraken_output = kraken_classification(fastp_output)
    tools_output = tools_output.concat(kraken_output)
  }

  if ( params.bowtie2 ) {
    bowtie_output = bowtie_classification(fastp_output, user_input)
    tools_output = tools_output.concat(bowtie_output)
  }

  if ( params.ganon2 ) {
    ganon_output = ganon_classification(fastp_output)
    tools_output = tools_output.concat(ganon_output)
  }

  // if ( params.additional_tool ) {
  //   additional_tool_output = additional_tool_classification(fastp_output)
  //   tools_output = tools_output.concat(additional_tool_output)
  // }
  
  tools_output = tools_output.concat(fastq_and_groundtruth.groundtruth)

  // conversion
  convert_output = convert(tools_output)

  // visualization
  visualize(convert_output.newick_file, convert_output.kraken_files)
}
