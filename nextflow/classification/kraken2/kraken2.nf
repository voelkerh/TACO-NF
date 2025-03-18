nextflow.enable.dsl=2

params.outdir = './results'
params.db = 'k2_standard_08gb_20230605'

// Download pre-built Kraken2 database
process DOWNLOAD_DB {
    storeDir './db'

    output:
        path '${params.db}'

    script:
        """
        mkdir '${params.db}'
        wget -O ${params.db}.tar.gz https://genome-idx.s3.amazonaws.com/kraken/${params.db}.tar.gz
        tar -zxvf ${params.db}.tar.gz -C ${params.db}
        """
}

// Extract kraken database archive and apply kraken2 to input file
process KRAKEN2_CLASSIFICATION {
    container 'https://depot.galaxyproject.org/singularity/kraken2%3A2.1.3--pl5321hdcf5f25_0'
    publishDir '${params.outdir}', mode:'copy'

    input:
        path fastq
        path kraken_db

    output:
        file '${fastq.baseName}.classified.fastq'

    script:
        """
        kraken2 --threads 4 --db ${kraken_db} --output ${fastq.baseName}.classified.fastq ${fastq}
        """
}

process GENERATE_CLASSIFICATION_REPORT {
    container 'https://depot.galaxyproject.org/singularity/kraken2%3A2.1.3--pl5321hdcf5f25_0'
    publishDir '${params.outdir}', mode:'copy'

    input:
        path kraken_in
        path kraken_db

    output:
        file '${kraken_in.baseName}.report'

    script:
        """
        kraken2 --threads 4 --db ${kraken_db} --report ${kraken_in.baseName}.report ${kraken_in}
        """
}

workflow kraken_classification {

    take:
        fastq

    main:
        database = DOWNLOAD_DB()
        KRAKEN2_CLASSIFICATION(fastq, database)
        GENERATE_CLASSIFICATION_REPORT(fastq, database)

    emit: GENERATE_CLASSIFICATION_REPORT.out
    
}
