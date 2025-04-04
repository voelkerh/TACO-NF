nextflow.enable.dsl = 2

include { process_sra_accessions } from './preparation/sra_accession_processing.nf'
include { fastp_multiqc_workflow } from './preparation/fastq_qc.nf'
include { kraken_classification } from './classification/kraken2/kraken2.nf'
include { bowtie_classification } from './classification/bowtie2/bowtie2.nf'
include { ganon_classification } from './classification/ganon2/ganon2.nf'
include { convert } from './conversion/conversion.nf'
include { visualize } from './visualization/visualization.nf'
// include { new_classification } from './classification/new_classification_tool/tool.nf'

params.pipeline_input = "./sample_files/pipeline_input/sra_accession.txt"

workflow {
  println("Project directory: ${projectDir}")
  input_channel = Channel.fromPath(params.pipeline_input)

  // preparation
  fastq_and_groundtruth = process_sra_accessions(input_channel)
  fastp_output = fastp_multiqc_workflow(fastq_and_groundtruth.fastq)

  // classification
  kraken_output = kraken_classification(fastp_output.fastq)
  bowtie_output = bowtie_classification(fastp_output.fastq, input_channel)
  ganon_output = ganon_classification(fastp_output.fastq)
  // new_classification_tool_output = new_classification(fastp_output.fastq)

  // conversion
  tool_outputs = kraken_output.concat(bowtie_output).concat(ganon_output).concat(fastq_and_groundtruth.groundtruth)
  // tool_outputs = kraken_output.report.concat(bowtie_output).concat(fastq_and_groundtruth.groundtruth)
  // tool_outputs = kraken_output.concat(bowtie_output).concat(ganon_output).concat(new_classification_tool_output).concat(fastq_and_groundtruth.groundtruth)

  convert_output = convert(tool_outputs)

  // visualization
  visualize(convert_output.newick_file, convert_output.kraken_files)
}
