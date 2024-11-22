nextflow.enable.dsl=2
include {groundtruth_workflow} from './groundtruth/accessionFetcher.nf'
include {fastp_multiqc_workflow} from './projektstudium_1_dataprocessing/processFasta.nf'
include {kraken_workflow} from './b34-taxonomic-classification-kraken2/kraken_workflowDSL2.nf'
include {mapping} from './mapping/main_namedworkflow.nf'
include {gt_converter} from './gtConverter.nf'
include {visualize} from './newickdash.nf'

params.inputDir = "input/"
inputChannel = Channel.fromPath(params.inputDir+'*.fq')

workflow{

  main:
    KrakenGT = gt_converter()
    groundtruth_workflow_out = groundtruth_workflow()
    fastp_output = fastp_multiqc_workflow(groundtruth_workflow_out.fastq)
    kraken_output = kraken_workflow(fastp_output.fastq)
    mapping_output = mapping(fastp_output.fastq)
    plot = visualize(kraken_output, mapping_output, KrakenGT) 

}
  
