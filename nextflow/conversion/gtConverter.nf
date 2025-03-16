nextflow.enable.dsl=2

params.input_file = '.preparation/ground_truth.txt'
params.output_dir = 'kraken_output_files'
params.store_dir = launchDir + 'store/groundtruth_workflow/'

process convertToKraken {
container params.python_container_path
containerOptions "--bind ${projectDir}:${projectDir}"
publishDir params.output_dir

    input:
    path input_file

    output:
    path "converted_out/converted.report"

    script:
    """
    python ${projectDir}/conversion/gtConverter.py ${input_file} converted_out ${baseDir}/visualization/Database/database.db
    """
}

workflow gt_converter{
  take:
    infile
  main:
    //input_file = file(params.input_file)
    gtkraken = convertToKraken(infile)
  emit:
    gtkraken
}