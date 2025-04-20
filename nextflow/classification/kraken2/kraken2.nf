nextflow.enable.dsl=2

params.outdir = 'output/classification'
params.kraken_workflow_store_dir = launchDir + 'store/3_kraken2/'

// Download pre-built Kraken2 database
process DOWNLOAD_DB {
    storeDir params.kraken_workflow_store_dir + '/db/'

    output:
        path("${params.kraken2_db}/"), emit: db

    script:
        """
        mkdir ${params.kraken2_db}
        wget -O ${params.kraken2_db}.tar.gz https://genome-idx.s3.amazonaws.com/kraken/${params.kraken2_db}.tar.gz
        tar -zxvf ${params.kraken2_db}.tar.gz -C ${params.kraken2_db}
        rm ${params.kraken2_db}.tar.gz
        """
}

// Classify reads with kraken2 based on downloaded database
process KRAKEN2_CLASSIFICATION {
    container file(params.kraken2_container_path)
    storeDir params.kraken_workflow_store_dir + '/classified/'
    publishDir params.outdir + '/kraken_results/', mode:'copy'

    input:
        path fastq
        path kraken_db

    output:
        path "${fastq.baseName}_kraken.fastq", emit: classified
        path "${fastq.baseName}_kraken.report", emit: report

    script:
        """
        kraken2 --threads 4 --db ${kraken_db} \
            --output ${fastq.baseName}_kraken.fastq \
            --report ${fastq.baseName}_kraken.report \
            ${fastq}
        """
}

workflow kraken_classification {

    take:
        fastq

    main:
        database = DOWNLOAD_DB()
        classification_out = KRAKEN2_CLASSIFICATION(fastq, database)

    emit:
        report = classification_out.report

}
