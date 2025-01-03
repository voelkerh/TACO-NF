nextflow.enable.dsl=2

params.input_file = '.ground_truth/ground_truth.txt'
params.output_dir = 'kraken_output_files'

process convertToKraken {
container params.python_container_path
publishDir params.output_dir

    input:
    path input_file

    output:
    path "converted_out"

    script:
    """
    python ${projectDir}/gt_converter/gtConverter.py ${input_file} converted_out ${baseDir}/database.db
    """
}

workflow gt_converter{
  main:
    input_file = file(params.input_file)
    gtkraken = convertToKraken(input_file)
  emit:
    gtkraken
}