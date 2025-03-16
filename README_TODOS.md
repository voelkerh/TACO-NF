# To Dos

### Kurzfristige TODOS:
- Rename modules and vars
  - Abgleich mit [Architektur](./Images/pipeline.png)
  [x] Erstelle Conversion folder (aus gt_converter folder)
    [x] Place TreeMerger
    - Place script folder - copied
    - Place Database folder - copied
    - Place krakentonewick.py - copied
- Check what is processFasta doing, check wich module it belongs to and WTF is https://github.com/OpenGene/fastp ??
- rename ground_truth(folder) to preparation
  - fix sra_accession.txt and workflow (remove refseq, was added for testing and never removed)
  
[x] rename taxonomy_tools to classification
  - add ganon here (see Mittelfristige Todos, Ganon Einbinden)
[x] rename newick_dash to visualization
  - (Henni) Überprüfung der DashApp Version
- check if gt_converter is still used nor got needed information else move/delete
  - also what it actually does and what its returning data
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