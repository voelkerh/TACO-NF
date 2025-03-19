// This workflow integrates the Ganon classification tool for WGS data.
// It is divided into three processes: database creation, read classification and report generation.
// Three parameters can be specified: The sequence file (required), the database file (required) and the report type (default 'abundance').

// try: nextflow run ganon_workflow.nf --sequence_file input/test_sequence_file.fastq --database_file input/GCA_000005845.2_ASM584v2_genomic.fna

params.sequence_file = null
params.database_file = null
params.report_type = 'abundance'

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

// Creates a custom Ganon database based on the input file.
process BUILD_DB {
    storeDir 'database' // Specifies output directory for database
    container params.ganon_container_path

    input:
        path database_input_file

    output:
        path 'ecoli_db.*'

    script:
        """
        ganon build-custom --input ${database_input_file} --db-prefix ecoli_db
        """
}

// Classifies the input sequence file against the specified database.
process GANON_CLASSIFICATION {
    storeDir 'output' // Specifies output directory for classification results
    container params.ganon_container_path

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
    storeDir 'reports' // Specifies output directory for classification reports
    container params.ganon_container_path

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
