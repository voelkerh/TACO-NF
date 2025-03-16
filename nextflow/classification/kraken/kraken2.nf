nextflow.enable.dsl=2

params.outdir = './results'
params.db = 'k2_standard_08gb_20230605'

// Der Eingabepfad wird als Kommandozeilenargument festgelegt
//input_path = file(params.input_path)

// Download-Prozess
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

// Eingabe: FASTQ-Dateien und die heruntergeladene Kraken-Datenbank
// Ausgabe: Klassifizierte FASTQ-Datei
// Prozess: Kraken-Datenbankarchiv wird extrahiert und Kraken2 wird auf die Eingabedatei angewendet
process KRAKEN2_CLASSIFICATION {
    container 'https://depot.galaxyproject.org/singularity/kraken2%3A2.1.3--pl5321hdcf5f25_0'
    publishDir '${params.outdir}', mode:'copy' // Die Ergebnisse des Kraken2-Prozesses werden in diesem Verzeichnis veröffentlicht

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

// Klassifikationsbericht-Prozess
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

workflow kraken_workflow {
    //fasta_ch = channel.fromPath("${input_path}/*.fastq")
    take: fasta_ch

    main:
        db_ch = DOWNLOAD_DB()
        KRAKEN2_CLASSIFICATION(fasta_ch, db_ch)
        GENERATE_CLASSIFICATION_REPORT(fasta_ch, db_ch)

    emit: GENERATE_CLASSIFICATION_REPORT.out
}
