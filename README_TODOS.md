# To Dos

### Kurzfristige TODOS:

- Klassifikationsparameter:
  [x] in Pipeline einbauen
  [x] in help dokumentieren

- Converter:
  [] Readme ergänzen: Verwendung verschiedener Datenbanken kann zu Inkonsistenzen in Darstellung führen
  [] Parameter --align_taxonomies einbauen und Logik im kraken2kraken converter anpassen
  [x] Parameter in --help dokumentieren

- bowtie2:
  [] Readme ergänzen: Wenn verwendet, wie muss user input angepasst werden?

- Datenbankparameter:
  [x] benennen
  [x] prüfen, wo sie richtig abgelegt werden
  [x] in help dokumentieren

- Dash:
  [] check, ob es pop up funktion gibt, die darauf hinweist, dass nur funktionsfähig, solange die pipeline im Hintergrund läuft + notwendige Inhalte in storeDir gespeichert, von da aus testbar: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/modal/ 

#### Finalize repository

- Check **refseq in pipeline input**: (Lucy prüft Optionen für refseq Download)
    --> !! refseq is required information for bowtie2. These are accession numbers for reference sequences for organisms provided by NCBI in the RefSeq Database (other than SRA Database). bowtie2.nf extracts these (! 1st row commentary needed / will be cut off) and downloads refseqs for specific organisms to map the reads to.
  - Decide: New process to find suitable refseq for sra accession or **change requirements in manuscript**!

  - Make **user specified input** for pipeline possible (sample_file if no parameter, otherwise use parameter as input?)

- Identify reasons for **visualization issues**: (Henni)
  - Tree representation has artefacts -> merged_newick_tree.txt probably has issues, possibly due to conversion from kraken
  - Check order of tree and heatmap for consistency
  - Check output for localhost / link

[x] Use **PEP-8** formatting for **all python files**
- Possibly use **linter** (Pylint?) (Henni checkt, ob sinnvoll) - Docstring da, wo Einsatz sinnvoll, nicht kategorisch überall.
- Final repository **cleanup**

#### Write documentation

[x] Harmonize **documentation for nextflow files**

- **document code files in repository** using DocString (Henni)
  [x] create_tax_db.py
  [x] test.py
  [x] taxdb.py
  [x] taxDBsqlite.py - check nochmal name Ausgabe
  [-] kraken_to_newick.py - check ob man mit Namen anders umgehen kann, damit sie visualisierung nicht zerhauen
  - newick_merger.py
  - main.py
  - abstract_converter.py
  - ganon_to_kraken.py
  - gt_to_kraken.py
  - sam_to_kraken.py
  - dash_app.py - check heatmap konsistenz und reihenfolge

- rename taxDBsqlite.py

[x] **Update README**: Makefile (überarbeitet Lucy), create_db für accession2taxid muss selbst erstellt werden (lässt sich nicht zuverlässig committen) dafür braucht es download, ablage und build Anleitung.


### Long-term TODOs:

- Create new datasets and make documented test runs for manuscript

- Finalize manuscript

- Create [CITATION.cff](CITATION.cff)

- Provide pipeline in new clean repository

- Contact all authors for manuscript feedback

- Hand in manuscript (NAR, BMC Bioinformatics or PLOS One)
