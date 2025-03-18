nextflow.enable.dsl = 2

workflow bowtie_classification {
    take:
    reads // probably not reads, but merged fastq
    pipeline_input

    main:
    refsq_out = EXTRACT_REFSEQ(pipeline_input)
    preparedFastaChannel = ACCESSIONS_TO_FASTAS(refsq_out.splitText { it.trim() })
    mergedFastaChannel = MERGE_FASTAS(preparedFastaChannel.preparedFasta.collect())

    hash = HASHING_FASTA_FILE(mergedFastaChannel)
    indexFiles = INDEX_REFERENCE(mergedFastaChannel, hash)
    mergedFq = MERGE_FASTQS(reads)
    // probably not needed
    output = MAP_READS(indexFiles, mergedFq)

    emit:
    output
}

// params.readPath = 'qc_output_data/' // probably no longer needed
// params.reads = 'qc_output_data/' // probably no longer needed

// Extract RefSeq Accessions from pipeline input
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

// Download FASTA files from NCBI RefSeq database
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

// Merge downloaded FASTA files
process MERGE_FASTAS {
    container params.bowtie2_container_path
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
}

// Create hash of FASTA file for unique identification
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

// Create Bowtie2 index for reference FASTA file, hash used for unique naming
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
        bowtie2-build ${fasta_file} index_data/\$(cat ${md5sum})/index 
        """
}

// !!! Currently we have a combined FASTQ as input, this is probably not needed and could produce errors
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

// Map reads from combined FASTQ to reference FASTA file
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
        bowtie2 -x ${index_files}/index -U ${reads} -S output.sam -p 40
        """
}
