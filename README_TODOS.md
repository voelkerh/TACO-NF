# To Dos

### Kurzfristige TODOS:

#### 1. Restructure modules to match [Architektur](./Images/pipeline.png)

[x] Create Conversion folder (aus gt_converter folder)
[x] Place TreeMerger
[x] Place script folder - copied
[x] Place Database folder - copied
[x] Place krakentonewick.py - Places Kraken_to_newick_converter folder from utils.

[x] Rename ground_truth(folder) to preparation

[x] Rename taxonomy_tools to classification

[x] Rename newick_dash to visualization

#### 2. Rename variables

- preparation:
  [x] Improve variable and process names in sra_accession_processing.nf

#### 3. Restructure Workflows

- sample_files:

  - Fix sra_accession.txt (= user input to pipeline) and workflow (remove refseq, was added for testing and never removed)
    --> !! refseq is required information for bowtie2. These are accession numbers for reference sequences for organisms provided by NCBI in the RefSeq Database (other than SRA Database). bowtie2.nf extracts these (! 1st row commentary needed / will be cut off) and downloads refseqs for specific organisms to map the reads to.
  - Decide: New process to find suitable refseq for sra accession or change requirements in manuscript!
    [x] Move sra_accession.txt to sample_files folder and update all references

- preparation folder:
  [x] Why own .gitignore? Integrate into global .gitignore
  [x] Check why ground_truth.txt here - if this is sample input (for testing) move to new examples folder.

  - Check what process_fasta.nf is doing, check which module it belongs to and WTF is https://github.com/OpenGene/fastp ?? --> QualityControl for fastq files, does not even process fasta files, thus renamed to fastq_qc-nf
  - **Check if multiqcChannel is needed in process_fasta.nf, treat error**

- classification folder:
  [x] Add ganon folder from ganon branch
  [x] Standardise formatting in ganon.nf
  [x] Integrate ganon into main workflow

  - Find out about ganon database file
  - Translate ganon comments into English, transfer to tools integration documentation in README.md
  - Check nextflow.config in ganon subfolder, integrate into main nextflow.config

  [x] Correct inputs for bowtie2.nf (1 missing) to handle error and worklfow def in bowtie2.nf

  - bowtie2.nf has a process, which merges fastq input files -> Currently we have a combined fastq from the preparation module as input, this will produce errors!

- conversion folder:
  - Check which files in database subfolder are still needed, keep only necessary ones (probably delete: datenbank.py, taxdb_dump.py, taxdb_mock.py, test.py)
  - Check if left over database scripts should be here or in appcontainer python subfolder
  - **Revise conversion.nf workflow, esp. container (BioPython, etc)** - Dienstag 18.03.
    [x] Rename subfolders and update references to files in conversion.nf
  - Check use and output of gt_converter in conversion folder, integrate into conversion.nf

[x] visualization folder:
[x] Delete copies of folders from visualization folder
[x] Check version of DashApp: Update script and delete unnecessary files
[x] Update newickdash.nf to visualization.nf without conversion subworkflows
[x] Revise visualization.nf with input from conversion module

- Update overall workflow.nf with new workflows

#### 4. Replace absolute with relative paths / check container files

- Replace in python_container.sif:
  - %files
    /home/davidkirchner/code/htwpipe/nextflow/appcontainer/pythonfiles /opt/pythonfiles relative pfad

### Mittelfristige TODOS:

- Ganon einbinden
- Refactor Code
  - Linter
  - Code Kommentieren (eine Art javaDoc / kDoc)

### Langfristige TODOS:

- Anwendung der Pipeline auf einige weitere Datensätze
- Kleine Testsuite mittels pytest-workflow
- Erstelle [CITATION.cff](CITATION.cff))
- Code cleanup
- Bereitstellung der Pipeline als sauberes repository

- Erstellung und Einreichung (bei BMC Bioinformatics oder PLOS One) eines
  Manuskripts
