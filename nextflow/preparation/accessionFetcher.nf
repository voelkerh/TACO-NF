nextflow.enable.dsl=2
params.groundtruth_in = launchDir+'/sra_accession.txt'
params.groundtruth_workflow_store_dir = launchDir + 'store/groundtruth_workflow/'


// This process takes the contents of sra_accessions.txt 
//and returns the sra_accesssion id's with which we can fetch the reads
process parseTXT {
  container "https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0"
  input: 
    path accession

  output:
    path "sra_cleaned.txt"

  script:
    """
    awk '{print \$1}' ${accession} | tail -n +2 | sed 's/,//' > sra_cleaned.txt
    """
}

//takes sra_cleaned accesssion and downloads the accesssions using sra_tools and outputs
//it to accessions folder
process fetch {
  container "https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0"
  storeDir params.groundtruth_workflow_store_dir + 'fetch'
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
//dumps the fastq files from the prefetched runs. Runs are a compressed sra format which contains
//sequences and tools neccesary to convert them to fastq
process fasterq {
  container "https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0"
  storeDir params.groundtruth_workflow_store_dir + 'fasterq'

  input:
    tuple path(srafile), val(numreads)

  output:
    tuple path("${srafile.getSimpleName()}.fastq"), val(numreads)

  script:
    """
    fasterq-dump ${srafile} -O outdir
    cat outdir/*.fastq > ${srafile.getSimpleName()}.fastq
    """
}

//takes one fastq file at a time and extracts the corresponding number of reads from
//the sra_accessions.txt. Then it transfers the amount of reads denoted in sra_accessions.txt
//to a new fastq_sampled.fastq file.
process reader {
  container "https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0"
storeDir params.groundtruth_workflow_store_dir + 'reader'
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


process groundtruth_gen {
container "https://depot.galaxyproject.org/singularity/entrez-direct%3A22.1--he881be0_0"

  storeDir params.groundtruth_workflow_store_dir + 'groundtruth_gen'
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
process mergeFastq {
  container "https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0"
  storeDir params.groundtruth_workflow_store_dir + 'mergeFastq'


  input:
    path infastq
  output:
    path "sampled.fastq"
  script:
  """
  cat *.fastq >> sampled.fastq
  """
}
process mergeGroundtruth {
  container "https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0"
  storeDir params.groundtruth_workflow_store_dir + 'mergeGroundtruth'
  publishDir launchDir
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

workflow groundtruth_workflow {
  take:
    infile

  main:
    output = parseTXT(infile)
    sra_cleaned = infile.splitCsv(header: true, strip: true)
    fetch_out = fetch(sra_cleaned)
    fasterq_out = fasterq(fetch_out)
    reader_out = reader(fasterq_out)
    groundtruth_out = groundtruth_gen(fasterq_out)
    merged_fastq = mergeFastq(reader_out.map {v -> v[0]}.collect())
    merged_groundtruth = mergeGroundtruth(groundtruth_out.collect())

  emit:
    fastq = merged_fastq
    groundtruth = merged_groundtruth
    SRAACC = output
}

workflow {
  groundtruth_workflow(params.groundtruth_in)
}
