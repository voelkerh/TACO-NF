# To Dos

### Next TODOs

- Identify reasons for **visualization issues**:
  - Dash App: Alignment of leaf ordner and heatmap order
  - kraken2kraken // taxonomy_aligner

- READEME überarbeiten:
  - Klassifikationsparameter und Datenbankparameter beschreiben und Beispielaufruf anpassen
  - Erklärung zu Convertern ergänzen: Verwendung verschiedener Datenbanken kann zu Inkonsistenzen in Darstellung führen
  - Ergänzen: Wenn bowtie2 verwendet, muss user input mit spezifizierten refseqs angepasst werden (    --> !! refseq is required information for bowtie2. These are accession numbers for reference sequences for organisms provided by NCBI in the RefSeq Database (other than SRA Database). bowtie2.nf extracts these (! 1st row commentary needed / will be cut off) and downloads refseqs for specific organisms to map the reads to.)

- Manuskript:
  - Change requirements for user input in manuscript (refseqs only needed, when bowtie2 is used)

- Dash:
  [] check, ob es pop up funktion gibt, die darauf hinweist, dass nur funktionsfähig, solange die pipeline im Hintergrund läuft + notwendige Inhalte in storeDir gespeichert, von da aus testbar: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/modal/ 

- Bei Testlauf mit Ganon2:
  - check für ganon2 alignment problem: running `ganon classify` or `ganon report` with `--ranks all`, the output will show all ranks used for classification and presented sorted by lineage (also available with `ganon report --sort lineage`): https://pirovc.github.io/ganon/outputfiles/#ganon-classify

### Long-term TODOs:

- Create new datasets and make documented test runs for manuscript

- Finalize manuscript

- Create [CITATION.cff](CITATION.cff)

- Provide pipeline in new clean repository

- Contact all authors for manuscript feedback

- Hand in manuscript (NAR, BMC Bioinformatics or PLOS One)
