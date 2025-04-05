nextflow.enable.dsl = 2

params.outdir = 'output/classification'
params.bowtie_workflow_store_dir = launchDir + 'store/4_bowtie2/'

// Extract RefSeq Accessions from pipeline input
process EXTRACT_REFSEQ {
    storeDir params.bowtie_workflow_store_dir + '/refseqs/'

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
    container file(params.entrez_direct_container_path)
    storeDir params.bowtie_workflow_store_dir + '/accessionsToFastas/'

    input:
        val accession

    output:
        path "prepared_${accession}.fasta", emit: preparedFasta

    script:
        """
        efetch -db nucleotide -id '${accession}' -format fasta > 'prepared_${accession}.fasta'
        """
}

// Merge downloaded FASTA files
process MERGE_FASTAS {
    container file(params.bowtie2_container_path)
    storeDir params.bowtie_workflow_store_dir + '/mergeFastas/'

    input:
        path fastaFiles

    output:
        path 'merged.fasta', emit: mergedFasta

    script:
        """
        cat *.fasta > merged.fasta
        """
}

// Create hash of FASTA file for unique identification
process HASHING_FASTA_FILE {
    container file(params.bowtie2_container_path)
    storeDir params.bowtie_workflow_store_dir + '/hashingFasta/'

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
    container file(params.bowtie2_container_path)
    storeDir params.bowtie_workflow_store_dir + '/indexReference/'

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


// Map reads from combined FASTQ to reference FASTA file
process MAP_READS {
    container file(params.bowtie2_container_path)
    storeDir params.bowtie_workflow_store_dir + '/mapReads/'
    publishDir params.outdir + '/bowtie_results/'

    input:
        path index_files
        path reads

    output:
        path 'bowtie2.sam', emit: resultSam

    script:
        """
        bowtie2 -x ${index_files}/index -U ${reads} -S bowtie2.sam -p 40
        """
}

// Main workflow for Bowtie2 classification
workflow bowtie_classification {
    take:
        reads
        pipeline_input

    main:
        refsq_out = EXTRACT_REFSEQ(pipeline_input)
        preparedFastaChannel = ACCESSIONS_TO_FASTAS(refsq_out.splitText { it.trim() })
        mergedFastaChannel = MERGE_FASTAS(preparedFastaChannel.preparedFasta.collect())

        hash = HASHING_FASTA_FILE(mergedFastaChannel)
        indexFiles = INDEX_REFERENCE(mergedFastaChannel, hash)
        output = MAP_READS(indexFiles, reads) 

    emit:
        output
}
