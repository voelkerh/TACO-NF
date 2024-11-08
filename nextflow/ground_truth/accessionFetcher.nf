nextflow.enable.dsl=2
params.in = launchDir+'/sra_accessions.txt'
accessiontext = channel.fromPath('sra_accessions.txt')


process parseTXT {
  input: 
    path("accession")

  output:
    file "test.txt"
  script:
    """
    awk '{print \$1}' $accession | tail -n +2 | sed 's/,//' > test.txt   
    """

}

process fetch {
  container "https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0"
// storeDir params.storeDir

  input:
    file acc

  output:
    path 'accessions/*'

  script:
    """
    prefetch --option-file $acc -O accessions
    """
}

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

process reader {
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
}

process mergeFastq {
  input:
    path infastq
  output:
    path "sampled.fastq"
  script:
  """
  cat *.fastq > sampled.fastq
  """
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
process mergeGroundtruth{
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
  output = parseTXT(Channel.fromPath(params.in))
  fetch_out = fetch(output)
  fasterq_out = fasterq(fetch_out.flatten())
  reader_out = reader(fasterq_out)
  groundtruth_out = groundtruth_gen(fasterq_out)
  mergeFastq(reader_out.collect())
  mergeGroundtruth(groundtruth_out.collect())

}

   
