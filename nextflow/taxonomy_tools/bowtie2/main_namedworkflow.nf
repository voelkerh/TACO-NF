nextflow.enable.dsl = 2

params.accessions = launchDir+'/ground_truth/ground_truth.txt' // Pfad zur Accessions-Datei
params.readPath = "qc_output_data/"
params.reads = "qc_output_data/"
//params.indexFiles = "index_data/d60d78578a8ceeed296d3ae069e93208/Lactobacillus_acidophilus_index.1.bt2"



/*
 * Referenzvorbereitungsprozess - Luke
 */
process extractRefSeq {
    input:
    path inputFile
    
    output:
    path 'refseqs.txt'

    script:
    """
    tail -n +2 ${inputFile} | cut -d, -f3 > refseqs.txt
    """
}

process AccessionsToFastas {
    container "https://depot.galaxyproject.org/singularity/entrez-direct%3A22.1--he881be0_0"

    storeDir "${workflow.projectDir}/store"

    input:
    val accession

    output:
    path "prepared_${accession}.fasta", emit: preparedFasta

    script:
    """
    efetch -db nucleotide -id "${accession}" -format fasta > "prepared_${accession}.fasta"
    """
}

process MergeFastas {
    //container"/var/tmp/projekt/mapping/var/share/mapping-container.sif"
    container"https://depot.galaxyproject.org/singularity/bowtie2%3A2.5.4--he96a11b_5"

    input:
    path fastaFiles

    output:
    path "merged.fasta", emit: mergedFasta

    script:
    """
    #//mkdir store
    cat *.fasta > merged.fasta
    """
    //"""
    //cat $fastaFiles > merged.fasta
    //"""

}

/*
 * Indexierungsprozess - Ben
 */


process HashingFastaFile {
    //container"/var/tmp/projekt/mapping/var/share/mapping-container.sif"
    container params.bowtie2_container_path

    input: 
    path fasta_file

    output:
    path "md5sum.txt", emit: md5txt
    
    script:
    """
    md5sum=\$(md5sum ${fasta_file} | cut -d ' ' -f 1) > md5sum.txt   
    """
}

process IndexReference {
    container params.bowtie2_container_path

    input:
    path fasta_file
    val md5sum

    output:
    path "index_data", emit: indexFiles

    script:
    
    """
    mkdir -p index_data/\$(cat ${md5sum})
    bowtie2-build $fasta_file index_data/\$(cat ${md5sum})/index 
    """
}


/*
 * Mapping-Prozess - Tom
 */

 //Channel.fromPath(params.reads1)

process MergeFastqs {
    //container"/var/tmp/projekt/mapping/var/share/mapping-container.sif"
    container params.bowtie2_container_path

    input:
    path fastqFiles

    output:
    path "merged.fq", emit: mergedFq

    script:
    """
    mkdir store_fq
    cat *.fq > merged.fq
    """

}

process MapReads {
    //container"/var/tmp/projekt/mapping/var/share/mapping-container.sif"
    container params.bowtie2_container_path
    publishDir "${workflow.projectDir}/output"

    input:
    path index_files
    path reads
    
    output:
    path "output.sam", emit: resultSam

    script:
    """
    bowtie2 -x $index_files/index -U $reads -S output.sam -p 40
    """
}

/*
 * Gesamtworkflow-Definition
 */
workflow mapping {
    take: 
    reads
    

    main:
    refsq_out = extractRefSeq(params.accessions)
    preparedFastaChannel = AccessionsToFastas(refsq_out.splitText() {it.trim()})
    mergedFastaChannel = MergeFastas(preparedFastaChannel.preparedFasta.collect())

    // -----------

    hash = HashingFastaFile(mergedFastaChannel)
    indexFiles = IndexReference(mergedFastaChannel, hash)
    mergedFq = MergeFastqs(reads)
    output = MapReads(indexFiles, mergedFq)


    //------------    
    emit: output

}

workflow {
    mapping(Channel.fromPath(params.readPath))
}


