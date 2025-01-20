nextflow.enable.dsl=2

println "Project directory: ${projectDir}"

include {groundtruth_workflow} from './ground_truth/accessionFetcher.nf'
include {fastp_multiqc_workflow} from './dataprocessing/processFasta.nf'
include {kraken_workflow} from './taxonomy_tools/kraken/kraken_workflowDSL2.nf'
include {mapping} from './taxonomy_tools/bowtie2/main_namedworkflow.nf'
include {gt_converter} from './gt_converter/gtConverter.nf'
include {visualize} from './newick_dash/newickdash.nf'

params.inputDir = "input/"
inputChannel = Channel.fromPath(params.inputDir+'*.fq')
params.groundtruth = "ground_truth/sra_accession.txt"


workflow{

  main:
    groundtruth_workflow_out = groundtruth_workflow(Channel.fromPath(params.groundtruth))
    KrakenGT = gt_converter(groundtruth_workflow_out.groundtruth)
    fastp_output = fastp_multiqc_workflow(groundtruth_workflow_out.fastq)
    kraken_output = kraken_workflow(fastp_output.fastq)
    mapping_output = mapping(fastp_output.fastq)
    //plot = visualize(kraken_output, mapping_output, KrakenGT.gtkraken)
    plot = visualize(kraken_output, mapping_output)
//concatonate the mapping outputs to enable easier adding of other tools
}
