nextflow.enable.dsl=2

params.outputDir = 'output/preparation'
params.fastq_qc_store_dir = launchDir + 'store/2_fastq_qc/'

// Quality filtering options
// Note: The options used below derive from the fastp library
// Refer to fastp documentation for detailed information
// on these options: https://github.com/OpenGene/fastp
params.disable_quality_filtering = ''   //enter --disable_quality_filtering="-Q" to disable quality filtering
params.qualified_quality_phred = ''     //enter --qualified_quality_phred="-q int" int: the quality value that a base is qualified. Default 15 means phred quality is qualified, default: 15.
params.unqualified_percent_limit = ''   //enter --unqualified_percent_limit="-u int" int: how many percents of bases are allowed to be unqualified (0~100). Default 40 means .
params.n_base_limit = ''                //enter --n_base_limit="-n int" if one read's number of N base is >n_base_limit, then this read/pair is discarded. Default is 5 (int [=5])
params.average_qual = ''                //enter --average_qual="-e int" if one read's average quality score <avg_qual, then this read/pair is discarded. Default 0 means no requirement (int [=0])

// Length filtering options
params.disable_length_filtering = ''    //enter --disable_length_filtering="-L" length filtering is enabled by default. If this option is specified, length filtering is disabled
params.length_required = ''             //enter --length_required="-l int" int: reads shorter than length_required will be discarded, default is 15.
params.length_limit = ''                //enter --length_limit="--length_limit="--length_limit int" int: reads longer than length_limit will be discarded, default 0 means no limitation.

//Low complexity filtering
params.low_complexity_filter = ''       //enter --low_complexity_filter="-y" enable low complexity filter. The complexity is defined as the percentage of base that is different from its next base (base[i] != base[i+1]).
params.complexity_threshold = ''        //enter --complexity_threshold="-Y int" int: the threshold for low complexity filter (0~100). Default is 30, which means 30% complexity is required.

// Use fastp for filtering and quality control of merged FASTQ file while generating JSON and HTML reports
process CLEAN {
  container file(params.fastp_container_path)
  publishDir params.outputDir+'/fastp_report_and_fastq', mode: 'copy', overwrite:true
  storeDir params.fastq_qc_store_dir + '/fastp_clean/'

  input:
    path fastq

  output:
    path "*_cleaned.fq", emit: fastq
    path "${fastq.baseName}_fastp_report/", emit: report

  script:
    """
    mkdir ${fastq.baseName}_fastp_report
    fastp -i ${fastq} -o ${fastq.baseName}_cleaned.fq ${params.disable_quality_filtering} --html ${fastq.baseName}_fastp_report/${fastq.baseName}_fastp.html --json ${fastq.baseName}_fastp_report/${fastq.baseName}_fastp.json
    """
}

// Create interactive HTML report from fastp QC reports
process MULTIQC {
  container file(params.multiqc_container_path)
  publishDir params.outputDir+'/multiqc_report', mode:'copy', overwrite:true
  storeDir params.fastq_qc_store_dir + '/multi_qc/'

  input:
    path fastpReports

  output:
    path 'multiqc_report.html'

  script:
    """
    multiqc ${fastpReports}
    """
}


workflow quality_control_workflow {
  take: fastpChannel

  main:
    fastpRes = CLEAN(fastpChannel)
    MULTIQC(fastpRes.report.collect())
  
  emit: 
    fastpRes.fastq.collect()
}
