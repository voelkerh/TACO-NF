nextflow.enable.dsl=2

// Parameters
params.outdir = './results'
params.db = 'k2_standard_08gb_20230605'


// Der Eingabepfad wird als Kommandozeilenargument festgelegt
//input_path = file(params.input_path)

// Download-Prozess
process download_db {
    storeDir "./db"
    output:
    path "${params.db}"
    script:
    """
    mkdir "${params.db}"
    wget -O ${params.db}.tar.gz https://genome-idx.s3.amazonaws.com/kraken/${params.db}.tar.gz
    tar -zxvf ${params.db}.tar.gz -C ${params.db}
    """
}

process kraken2_process {

    container 'https://depot.galaxyproject.org/singularity/kraken2%3A2.1.3--pl5321hdcf5f25_0'

    // Die Ergebnisse des Kraken2-Prozesses werden in diesem Verzeichnis veröffentlicht
    publishDir "${params.outdir}", mode:'copy'

    input:
    // Eingabepfade für FASTQ-Dateien und die heruntergeladene Kraken-Datenbank
    path fastq
    path kraken_db

    output:
    // Der Ausgabepfad für die klassifizierte FASTQ-Datei
    file "${fastq.baseName}.classified.fastq"

    script:
    // Das Kraken-Datenbankarchiv wird extrahiert und Kraken2 wird auf die Eingabedatei angewendet
    """
    kraken2 --threads 4 --db ${kraken_db} --output ${fastq.baseName}.classified.fastq ${fastq}
    """
}

// Klassifikationsbericht-Prozess
process classify_report_process {
    container 'https://depot.galaxyproject.org/singularity/kraken2%3A2.1.3--pl5321hdcf5f25_0'
    publishDir "${params.outdir}", mode:'copy'
    input:
    path kraken_in
    path kraken_db
    output:
    file "${kraken_in.baseName}.report" 
    script:
    """
    kraken2 --threads 4 --db ${kraken_db} --report ${kraken_in.baseName}.report ${kraken_in}
    """
}


// Workflow
workflow kraken_workflow{
    //fasta_ch = channel.fromPath("${input_path}/*.fastq")
    take: fasta_ch

    main:
        db_ch = download_db()
        kraken2_process(fasta_ch, db_ch)
        classify_report_process(fasta_ch, db_ch)

    emit: classify_report_process.out
}
