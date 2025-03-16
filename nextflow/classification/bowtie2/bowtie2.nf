nextflow.enable.dsl = 2

params.accessions = launchDir+'/preparation/sra_accession.txt' // Pfad zur Accessions-Datei
params.readPath = 'qc_output_data/'
params.reads = 'qc_output_data/'

// Referenzvorbereitungsprozess - Luke
process EXTRACT_REFSEQ {
    input:
    path inputFile
    
    output:
    path 'refseqs.txt'

    script:
    """
    tail -n +2 ${inputFile} | cut -d, -f3 > refseqs.txt
    """
}

process ACCESSIONS_TO_FASTAS {
    container params.entrez_direct_container_path
    storeDir '${workflow.projectDir}/store/AccessionsToFastas'

    input:
    val accession

    output:
    path 'prepared_${accession}.fasta', emit: preparedFasta

    script:
    """
    efetch -db nucleotide -id '${accession}'' -format fasta > 'prepared_${accession}.fasta'
    """
}

process MERGE_FASTAS {
    container 'https://depot.galaxyproject.org/singularity/bowtie2%3A2.5.4--he96a11b_5'
    storeDir '${workflow.projectDir}/store/MergeFastas'

    input:
    path fastaFiles

    output:
    path 'merged.fasta', emit: mergedFasta

    script:
    """
    #//mkdir store
    cat *.fasta > merged.fasta
    """
    //"""
    //cat $fastaFiles > merged.fasta
    //"""
}

// Indexierungsprozess - Ben
process HASHING_FASTA_FILE {
    container params.bowtie2_container_path

    input: 
    path fasta_file

    output:
    path 'md5sum.txt', emit: md5txt
    
    script:
    """
    md5sum=\$(md5sum ${fasta_file} | cut -d ' ' -f 1) > md5sum.txt   
    """
}

process INDEX_REFERENCE {
    container params.bowtie2_container_path

    input:
    path fasta_file
    val md5sum

    output:
    path 'index_data', emit: indexFiles

    script:
    
    """
    mkdir -p index_data/\$(cat ${md5sum})
    bowtie2-build $fasta_file index_data/\$(cat ${md5sum})/index 
    """
}


// Mapping-Prozess - Tom
process MERGE_FASTQS {
    container params.bowtie2_container_path

    input:
    path fastqFiles

    output:
    path 'merged.fq', emit: mergedFq

    script:
    """
    mkdir store_fq
    cat *.fq > merged.fq
    """
}

process MAP_READS {
    container params.bowtie2_container_path
    publishDir '${workflow.projectDir}/output'

    input:
    path index_files
    path reads
    
    output:
    path 'output.sam', emit: resultSam

    script:
    """
    bowtie2 -x $index_files/index -U $reads -S output.sam -p 40
    """
}

workflow mapping {
    take: 
    reads
    ground_truth_file
    
    main:
    refsq_out = EXTRACT_REFSEQ(ground_truth_file)
    preparedFastaChannel = ACCESSIONS_TO_FASTAS(refsq_out.splitText() {it.trim()})
    mergedFastaChannel = MERGE_FASTAS(preparedFastaChannel.preparedFasta.collect())

    hash = HASHING_FASTA_FILE(mergedFastaChannel)
    indexFiles = INDEX_REFERENCE(mergedFastaChannel, hash)
    mergedFq = MERGE_FASTQS(reads)
    output = MAP_READS(indexFiles, mergedFq)
    
    emit: output
}

workflow {
    mapping(Channel.fromPath(params.readPath))
}


