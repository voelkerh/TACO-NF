nextflow.enable.dsl=2

params.user_input = projectDir + '/sample_files/pipeline_input/sra_accession.txt'
params.groundtruth_workflow_store_dir = launchDir + 'store/1_sra_accession_processing/'

// This process takes the contents of sra_accessions.txt 
//and returns the sra_accesssion id's with which we can fetch the reads
process EXTRACT_SRA_ACCESSION_FROM_USER_INPUT {
  container file(params.sra_tools_container_path)
  storeDir params.groundtruth_workflow_store_dir + '/extract_sra_accessions/'

  input: 
    path accession

  output:
    path "sra_cleaned.txt"

  script:
    """
    awk '{print \$1}' ${accession} | tail -n +2 | sed 's/,//' > sra_cleaned.txt
    """
}

// This process fetches raw sequence data from the NCBI SRA database using the sra_tools with isolated SRA accessions.
// We use SRR accessions (means Run accession -> single sequencing file / fastq of one run).
process FETCH_RAW_SEQUENCE_DATA {
  container file(params.sra_tools_container_path)
  storeDir params.groundtruth_workflow_store_dir + '/fetch_raw_sequence_data/'
  // Make sure that only one download runs in parallel so NCBI does not blacklist us
  maxForks 1

  input:
    tuple val(accession), val(numreads), val(refseq)

  output:
    tuple path("${accession}.sra"), val(numreads)

  script:
    """
    prefetch ${accession}
    mv ${accession}/${accession}.sra .
    """
}

// This process takes the .sra files and converts them to fastq files using the fasterq-dump tool from sratools.
process SRA_TO_FASTQ_WITH_FASTERQ {
  container file(params.sra_tools_container_path)
  storeDir params.groundtruth_workflow_store_dir + '/fastq_from_sra_with_fasterq/'

  input:
    tuple path(srafile), val(numreads)

  output:
    tuple path("${srafile.getSimpleName()}.fastq"), val(numreads)

  script:
    """
    fasterq-dump ${srafile}
    cat *.fastq > ${srafile.getSimpleName()}.fastq
    """
}

// Based on the number of reads specified in the user input, this process extracts the corresponding number of reads from the fastq file.
// Then it transfers these reads to a new fastq_sampled.fastq file.
process GENERATE_FASTQ_WITH_SPECIFIED_READNUMBER {
  container file(params.sra_tools_container_path)
  storeDir params.groundtruth_workflow_store_dir + '/fastq_with_specified_read_number/'

  input:
    tuple path(fastq), val(numreads)

  output:
    tuple path("${fastq.baseName}_sampled_${numreads}.fastq"), val(numreads)

  script:
  // store dir
    """
    head -n \$((4*${numreads})) ${fastq} > ${fastq.baseName}_sampled_${numreads}.fastq
    """
  //4*numreads because one read in fastq file contains 4 lines
}

// This process fetches the taxid for a single SRA accession using the entrez-direct tool.
// It then generates the basis for the groundtruth file including the taxid and the number of reads.
process GENERATE_GROUND_TRUTH_BASIS {
  container file(params.entrez_direct_container_path)
  storeDir params.groundtruth_workflow_store_dir + '/groundtruth_with_taxid/'

  input:
    tuple path(fastq), val(numreads)

  output:
    path "${fastq.getSimpleName()}_${numreads}_groundtruth.txt"

  script:
    """
    accession=${fastq.getSimpleName()}
    efetch -db sra -id \$accession -format xml > accession.xml
    taxid=`cat accession.xml | grep -hnr "tax_id" | grep -o 'tax_id="[0-9]*"' | sed 's/tax_id="//; s/"//' | head -n 1`
    echo \$taxid, $numreads > \${accession}_${numreads}_groundtruth.txt
    """
}

// This process merges the fastq files generated in the previous process into a single fastq file.
// The output serves as artificial metagenomic sample.
process MERGE_FASTQ {
  container file(params.sra_tools_container_path)
  storeDir params.groundtruth_workflow_store_dir + '/mergeFastq/'

  input:
    path infastq

  output:
    path "merged.fastq"

  script:
  """
  cat *.fastq >> merged.fastq
  """
}

// This process merges the groundtruth bases generated in the previous process into a single groundtruth file.
// This file contains the taxid and the number of reads for each SRA accession.
process MERGE_GROUND_TRUTH {
  container file(params.sra_tools_container_path)
  storeDir params.groundtruth_workflow_store_dir + '/mergeGroundTruth/'

  input:
    path accessiontxt

  output:
    path "groundtruth.txt"

  script:
    """
    echo "taxid, readnumber" > groundtruth.txt
    cat *_*.txt >> groundtruth.txt
    """
}

workflow process_sra_accessions {
  take:
    infile

  main:
    //output = EXTRACT_SRA_ACCESSION_FROM_USER_INPUT(infile)
    sra_cleaned = infile.splitCsv(header: true, strip: true)
    sra_raw_data = FETCH_RAW_SEQUENCE_DATA(sra_cleaned)
    fasterq_out = SRA_TO_FASTQ_WITH_FASTERQ(sra_raw_data)
    customized_fastq = GENERATE_FASTQ_WITH_SPECIFIED_READNUMBER(fasterq_out)
    groundtruth_basis = GENERATE_GROUND_TRUTH_BASIS(fasterq_out)
    merged_fastq = MERGE_FASTQ(customized_fastq.map {v -> v[0]}.collect())
    merged_groundtruth = MERGE_GROUND_TRUTH(groundtruth_basis.collect())

  emit:
    fastq = merged_fastq
    groundtruth = merged_groundtruth
    //SRAACC = output
}
