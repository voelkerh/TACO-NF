nextflow.enable.dsl=2

// println 'Project directory: ${projectDir}'

include {groundtruth_workflow} from './preparation/sra_accession_processing.nf'
include {fastp_multiqc_workflow} from './preparation/process_fasta.nf'
include {kraken_workflow} from './classification/kraken2/kraken2.nf'
include {mapping} from './classification/bowtie2/bowtie2.nf'
include {gt_converter} from './conversion/gtConverter.nf'
include {visualize} from './visualization/visualization.nf'

// params.inputDir = "input/"
// inputChannel = Channel.fromPath(params.inputDir+'*.fq')
params.groundtruth = "preparation/sra_accession.txt"

workflow {

  main:
    ground_truth_file = Channel.fromPath(params.groundtruth)
    groundtruth_workflow_out = groundtruth_workflow(ground_truth_file)
    KrakenGT = gt_converter(groundtruth_workflow_out.groundtruth)
    fastp_output = fastp_multiqc_workflow(groundtruth_workflow_out.fastq)
    kraken_output = kraken_workflow(fastp_output.fastq)
    mapping_output = mapping(fastp_output.fastq, ground_truth_file)
    tool_outputs = kraken_output.concat(mapping_output).concat(KrakenGT.gtkraken)
    //plot = visualize(kraken_output, mapping_output, KrakenGT.gtkraken)
    plot = visualize(tool_outputs)
    //concatonate the mapping outputs to enable easier adding of other tools
    
}
