nextflow.enable.dsl=2

params.inputDir = "input/"
inputChannel = Channel.fromPath(params.inputDir+'*.fq')

process gt_generator {
    input:

    output:

    script:


}

process gt_to_kraken {
    input:

    output:

    script:

    
}

process gt_to_fastq {
    input:

    output:

    script:

    
}

process bowtie2 {
    input:

    output:

    script:

    
}

process kraken2 {
    input:

    output:

    script:

    
}

process sam_to_kraken {
    input:

    output:

    script:

    
}

process visualize {
    input:

    output:

    script:


}

workflow{

  main:

    ground_truth = gt_generator()
    ground_truth_kraken = gt_converter(ground_truth)
    ground_truth_fastq = gt_to_fastq(ground_truth)
    
    bowtie2_result = bowtie2(ground_truth_fastq)
    kraken2_result = kraken2(ground_truth_fastq)

    plot = visualize(bowtie2_result, kraken2_result, ground_truth_kraken)

}
  
