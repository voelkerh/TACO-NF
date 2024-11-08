nextflow.enable.dsl=2

params.input_file = 'groundtruth.txt'
params.output_dir = 'kraken_output_files'

process convertToKraken {
container '/var/tmp/projekt/singularity_containers/my-python-container.sif'
publishDir params.output_dir

    input:
    path input_file

    output:
    path "converted_out"

    script:
    """
    python /var/tmp/projekt/gtConverter.py ${input_file} converted_out ${baseDir}/database.db
    """
}

workflow gt_converter{
  main:
    input_file = file(params.input_file)
    gtkraken = convertToKraken(input_file)
  emit:
    gtkraken
}


