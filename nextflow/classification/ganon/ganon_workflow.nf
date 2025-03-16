// Dieser Workflow nutzt Nextflow, um DNA-Sequenzierungsdaten mit Ganon zu analysieren. 
// Er besteht aus drei Hauptprozessen: dem Erstellen einer Datenbank, dem Klassifizieren von Sequenzen und dem Generieren eines Berichts.

// Die folgenden Parameter können von der Kommandozeile übergeben werden:
// - sequence_file: Die Eingabesequenzdatei, die klassifiziert werden soll.
// - database_file: Die Datei, die als Eingabe für den Datenbankaufbau dient.
// - report_type: Der Typ des Berichts, der generiert werden soll (Standard: 'abundance').

// try: nextflow run ganon_workflow.nf --sequence_file input/test_sequence_file.fastq --database_file input/GCA_000005845.2_ASM584v2_genomic.fna

params.sequence_file = null  // Datei mit Sequenzdaten, erforderlich
params.database_file = null  // Datei mit Datenbankeingaben, erforderlich
params.report_type = 'abundance'  // Standardwert für den Berichtstyp

// Prozess: build_database
// Dieser Prozess erstellt eine benutzerdefinierte Ganon-Datenbank aus der angegebenen Eingabedatei.
process build_database {
    storeDir "database"  // Der Prozess speichert alle Ausgaben im Verzeichnis "database"
    container "https://depot.galaxyproject.org/singularity/ganon:2.1.0--py39ha35b9be_0"  // Singularity-Container mit der Ganon-Software

    output:
    path "ecoli_db.*"  // Alle Dateien mit diesem Präfix werden als Ausgabe bereitgestellt

    input:
    path database_input_file  // Die Eingabedatei für den Datenbankaufbau

    script:
    """
    ganon build-custom --input $database_input_file --db-prefix ecoli_db    
    """
}       

// Prozess: classify
// Dieser Prozess klassifiziert die Sequenzdateien gegen die zuvor erstellte Ganon-Datenbank.
process classify {
    storeDir "output"  // Speichert die Ausgaben im Verzeichnis "output"
    container "https://depot.galaxyproject.org/singularity/ganon:2.1.0--py39ha35b9be_0"  // Singularity-Container mit Ganon

    input:
    path test_sequence_file  // Die Sequenzdatei, die klassifiziert werden soll
    path database  // Die Datenbank, die im vorherigen Prozess erstellt wurde

    output:
    path "classification_output.*"  // Alle Dateien mit diesem Präfix werden als Ausgabe bereitgestellt

    script:
    """
    ganon classify --db-prefix ecoli_db --single-reads $test_sequence_file --output-prefix classification_output
    """
}

// Prozess: generate_report
// Dieser Prozess generiert einen Bericht basierend auf den Klassifikationsergebnissen und der Datenbank.
process generate_report {
    storeDir "reports"  // Speichert die Ausgaben im Verzeichnis "reports"
    container "https://depot.galaxyproject.org/singularity/ganon:2.1.0--py39ha35b9be_0"  // Singularity-Container mit Ganon

    input:
    path class_file  // Die Klassifikationsergebnisse aus dem vorherigen Prozess
    path database  // Die verwendete Datenbank
    val report_type  // Der Berichtstyp (z. B. 'abundance')

    output:
    path "classification_report_*.tre"  // Generiert Berichte mit diesem Präfix

    script:
    """
    ganon report --db-prefix ecoli_db --input classification_output.rep --output-prefix classification_report_$report_type --report-type $report_type
    """
}

// Hauptworkflow
workflow {
    // Prüfen, ob die erforderlichen Parameter übergeben wurden
    if (!params.sequence_file || !params.database_file) {
        error "Bitte gib sowohl 'sequence_file' als auch 'database_file' als Parameter an."
    }

    // Definieren der Eingabedateien
    test_sequence_file = file(params.sequence_file)  // Eingabesequenzdatei
    database_input_file = file(params.database_file)  // Datenbankeingabedatei

    // Workflow-Pipeline
    // 1. Erstelle die Datenbank
    database = build_database(database_input_file) 

    // 2. Klassifiziere die Sequenzdateien gegen die Datenbank
    classification = classify(test_sequence_file, database) 

    // 3. Generiere einen Bericht basierend auf den Klassifikationsergebnissen
    generate_report(classification, database, params.report_type)
}
