nextflow.enable.dsl=2

params.user_input = projectDir + '/sample_files/pipeline_input/sra_accession.txt'
params.groundtruth_workflow_store_dir = launchDir + 'store/1_sra_accession_processing/'

// Fetch raw sequence data from the NCBI SRA database using sratools with isolated SRA accession IDs
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

// Convert .sra files to FASTQ files using the fasterq-dump tool from sratools
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

// Extract the number of reads specified in the user input from the FASTQ file and save to new sampled FASTQ file
process GENERATE_FASTQ_WITH_SPECIFIED_READNUMBER {
  container file(params.sra_tools_container_path)
  storeDir params.groundtruth_workflow_store_dir + '/fastq_with_specified_read_number/'

  input:
    tuple path(fastq), val(numreads)

  output:
    tuple path("${fastq.baseName}_sampled_${numreads}.fastq"), val(numreads)

  script:
    """
    head -n \$((4*${numreads})) ${fastq} > ${fastq.baseName}_sampled_${numreads}.fastq
    """
  //4*numreads because one read in fastq file contains 4 lines
}

// Fetch taxid for single SRA accession ID using entrez-direct tool
// Generate basis for the groundtruth file based on taxid and number of reads
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

// Merge generated FASTQ files into a single FASTQ file, representing an artificial metagenomic sample
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

// Merges groundtruth bases into single groundtruth file, consisting of taxid and number of reads for each SRA accession
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
    sra_cleaned = infile.splitCsv(header: true, strip: true) // Extract SRA accesssion IDs to fetch the reads with
    sra_raw_data = FETCH_RAW_SEQUENCE_DATA(sra_cleaned)
    fasterq_out = SRA_TO_FASTQ_WITH_FASTERQ(sra_raw_data)
    customized_fastq = GENERATE_FASTQ_WITH_SPECIFIED_READNUMBER(fasterq_out)
    groundtruth_basis = GENERATE_GROUND_TRUTH_BASIS(fasterq_out)
    merged_fastq = MERGE_FASTQ(customized_fastq.map {v -> v[0]}.collect())
    merged_groundtruth = MERGE_GROUND_TRUTH(groundtruth_basis.collect())

  emit:
    fastq = merged_fastq
    groundtruth = merged_groundtruth
}
