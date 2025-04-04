// This workflow integrates the Ganon classification tool for WGS data.
// It is divided into three processes: database creation, read classification and report generation.
// Three parameters can be specified: The sequence file (required), the database file (required) and the report type (default 'abundance').

params.outdir = 'output'
params.db = 'archaea bacteria fungi viral'
params.ganon_workflow_store_dir = launchDir + 'store/5_ganon/'

params.sequence_file = null
params.database_file = null
params.report_type = 'abundance'

// Creates a custom Ganon database based on the input file.
process BUILD_DB {
    container file(params.ganon_container_path)
    storeDir params.ganon_workflow_store_dir + '/db/'

    output:
        path 'ganon_database.*'

    script:
        """
        ganon build --source refseq --organism-group ${params.db} --threads 48 --complete-genomes --db-prefix ganon_database
        """
}

// Classifies the input sequence file against the specified database.
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

// Generates a classification report based on the classification results and database.
process GENERATE_REPORT {
    container file(params.ganon_container_path)
    storeDir params.ganon_workflow_store_dir + '/reports/'
    publishDir params.outdir + '/ganon_results/'

    input:
        path classification_output
        path database
        val report_type

    output:
        path 'classification_report_*.tre'

    script:
        """
        ganon report --db-prefix ${database} --input ${classification_output} --output-prefix classification_report_${report_type} --report-type ${report_type}
        """
}

// Main workflow for Ganon classification
// It takes a sequence file and a database file as input, and generates a classification report.
workflow ganon_classification {
    take:
        sequence_file

    main:
        database_file = params.database_file
        sequence_file.view()
        // database_file.view()

        // 1. Create the database
        database = BUILD_DB(database_file)

        // 2. Classify the sequence files against the database
        classification_output = GANON_CLASSIFICATION(sequence_file, database)

        // 3. Generate a report based on the classification results
        report_output = GENERATE_REPORT(classification_output, database, params.report_type)

    emit:
        classification_output
        report_output
}
