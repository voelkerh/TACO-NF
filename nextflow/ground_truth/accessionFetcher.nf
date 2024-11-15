nextflow.enable.dsl=2
params.in = launchDir+'/sra_accessions.txt'
accessiontext = channel.fromPath('sra_accessions.txt')
// taucht nur einmal auf?


// This process takes the contents of sra_accessions.txt 
//and returns the sra_accesssion id's with which we can fetch the reads
process parseTXT {
  container "https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0"
  input: 
    path("accession")

  output:
    file "sra_cleaned.txt"
  script:
    """
    awk '{print \$1}' $accession | tail -n +2 | sed 's/,//' > sra_cleaned.txt   
    """

}

//takes sra_cleaned accesssion and downloads the accesssions using sra_tools and outputs
//it to accessions folder
process fetch {
  container "https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0"
// storeDir params.storeDir

  input:
    file sra_cleaned

  output:
    path 'accessions/*'

  script:
    """
    prefetch --option-file $sra_cleaned -O accessions
    """
}
//dumps the fastq files from the prefetched runs. Runs are a compressed sra format which contains
//sequences and tools neccesary to convert them to fastq
process fasterq {
  container "https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0"

  input:
    path accessions

  output:
    path 'fasterqs/*_1.fastq'

  script:
    """
    fasterq-dump ${accessions} -O fasterqs
    """
}

//takes one fastq file at a time and extracts the corresponding number of reads from 
//the sra_accessions.txt. Then it transfers the amount of reads denoted in sra_accessions.txt
//to a new fastq_sampled.fastq file. 
process reader {
  container "https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0"
  input:
    path fastq
  output:
    path "${fastq.baseName}_sampled.fastq"
  script:
    """
    fastq_name=${fastq}
    accession=\${fastq_name%_*}
    numreads=`cat ${params.in} | tail -n +2 | grep \$accession | cut -d , -f 2`
    head -n \$((4*numreads)) ${fastq} > ${fastq.baseName}_sampled.fastq
    """
    //4*numreads because one read in fastq file contains 4 lines
}


process groundtruth_gen{
container "https://depot.galaxyproject.org/singularity/entrez-direct%3A22.1--he881be0_0"

  input:
    path fastq
  output:
    path "*.txt"

  script:
    """
    fastq_name=${fastq}
    accession=\${fastq_name%_*}
    #echo \$accession 
    efetch -db sra -id \$accession -format xml > accession.xml
    taxid=`cat accession.xml | grep -hnr "tax_id" | grep -o 'tax_id="[0-9]*"' | sed 's/tax_id="//; s/"//' | head -n 1`
    numreads=`cat ${params.in} | tail -n +2 | grep \$accession | cut -d , -f 2`
    echo \$taxid, \$numreads > \${accession}_groundtruth.txt

    
    
    """
}
process mergeFastq {
  container "https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0"
  input:
    path infastq
  output:
    path "sampled.fastq"
  script:
  """
  cat *.fastq >> sampled.fastq
  """
}
process mergeGroundtruth{
  container "https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0"
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
  //take:

  main:
    output = parseTXT(Channel.fromPath(params.in))
    fetch_out = fetch(output)
    fasterq_out = fasterq(fetch_out.flatten())
    reader_out = reader(fasterq_out)
    groundtruth_out = groundtruth_gen(fasterq_out)
    merged_fastq = mergeFastq(reader_out.collect())
    merged_groundtruth = mergeGroundtruth(groundtruth_out.collect())

  emit:
    fastq = merged_fastq
    groundtruth = merged_groundtruth
    SRAACC = output
}

workflow {
  //parseTXT(params.in) | fetch | flatten | fasterq | reader | collect | mergeFastq
  sra_cleaned = parseTXT(Channel.fromPath(params.in))
  fetch_out = fetch(sra_cleaned)
  fasterq_out = fasterq(fetch_out.flatten())
  reader_out = reader(fasterq_out)
  groundtruth_out = groundtruth_gen(fasterq_out)
  mergeFastq(reader_out.collect())
  mergeGroundtruth(groundtruth_out.collect())

}

   
