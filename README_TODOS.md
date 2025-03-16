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
- preparation folder:
  [x] Why own .gitignore? Integrate into global .gitignore
  [x] Check why ground_truth.txt here - if this is sample input (for testing) move to new examples folder.
  - Fix sra_accession.txt (= user input to pipeline) and workflow (remove refseq, was added for testing and never removed)
  - Move sra_accession.txt to sample_files folder and update all references
  - Check what process_fasta.nf is doing, check which module it belongs to and WTF is https://github.com/OpenGene/fastp ??

- classification folder:
  [x] Add ganon folder from ganon branch
  [x] Standardise formatting in ganon.nf
  - integrate ganon into main workflow

- conversion folder:
  - **Create new conversion.nf workflow based on subfolders, use visualization/newickdash.nf as reference** - Dienstag 18.03.
  - Rename subfolders and update references to files in conversion.nf
  - Check use and output of gt_converter in conversion folder, integrate into conversion.nf

- visualization folder:
  [x] Delete copies of folders from visualization folder
  - Check version of DashApp: Update script and delete unnecessary files
  [x] Update newickdash.nf to visualization.nf without conversion subworkflows
  - Revise visualization.nf with input from conversion module

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