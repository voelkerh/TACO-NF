nextflow.enable.dsl = 2

params.outdir = 'output/classification'
params.ganon_workflow_store_dir = launchDir + 'store/5_ganon/'

params.db = ['archaea', 'bacteria', 'fungi', 'viral']
params.report_type = 'abundance'

// Create a custom Ganon database based on params.db
process BUILD_DB {
    container file(params.ganon_container_path)
    storeDir params.ganon_workflow_store_dir + '/db/'

    output:
        path 'ganon_database.*'

    script:
        """
        ganon build --source refseq --organism-group ${params.db.join(',')} --threads 48 --complete-genomes --db-prefix ganon_database
        """
}

// Classify FASTQ file using custom database
process GANON_CLASSIFICATION {
    container file(params.ganon_container_path)
    storeDir params.ganon_workflow_store_dir + '/classification/'
    publishDir params.outdir + '/ganon_results/'

    input:
        path test_sequence_file // Sequence file to be classified
        path database

    output:
        path 'classification_output.*'

    script:
        """
        ganon classify --db-prefix ${database} --single-reads ${test_sequence_file} --output-prefix classification_output
        """
}

// Generate classification report based on classification results and database
process GENERATE_REPORT {
    container file(params.ganon_container_path)
    storeDir params.ganon_workflow_store_dir + '/reports/'
    publishDir params.outdir + '/ganon_results/'

    input:
        path classification_output
        path database

    output:
        path "classification_report_*.tre", emit: report

    script:
        """
        ganon report --db-prefix ${database} --input ${classification_output} --output-prefix classification_report_${params.report_type} --report-type ${params.report_type}
        """
}

workflow ganon_classification {
    take:
        sequence_file

    main:
        database = BUILD_DB()
        classification_output = GANON_CLASSIFICATION(sequence_file, database)
        report = GENERATE_REPORT(classification_output, database)

    emit:
        report
}
