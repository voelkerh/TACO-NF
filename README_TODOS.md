# To Dos

### Kurzfristige TODOS:

#### 1. Restructure modules to match architecture in manuscript - Done

#### 2. Rename variables - Done

#### 3. Restructure Workflows - Done

#### 4. Update container definitions and makefile - Done

### Further TODOs:

#### Finalize repository

- Check **refseq in pipeline input**: (Lucy prüft Optionen für refseq Download)
    --> !! refseq is required information for bowtie2. These are accession numbers for reference sequences for organisms provided by NCBI in the RefSeq Database (other than SRA Database). bowtie2.nf extracts these (! 1st row commentary needed / will be cut off) and downloads refseqs for specific organisms to map the reads to.
  - Decide: New process to find suitable refseq for sra accession or **change requirements in manuscript**!
  - Make **user specified input** for pipeline possible (sample_file if no parameter, otherwise use parameter as input?)

- Ganon2: Database changes have been made, needs to be tested

- Bowtie2: MergeFastq was not need and was changed, need to be tested

- Identify reasons for **visualization issues**: (Henni)
  - Tree representation has artefacts -> merged_newick_tree.txt probably has issues, possibly due to conversion from kraken
  - Check order of tree and heatmap for consistency
  - Check output for localhost / link

- Write **test suite** with pytest workflow (erstmal nicht, wenn dann converter test suite für user)

- Use **PEP-8** formatting for **all python files** hat Henni gemacht
- Possibly use **linter** (Pylint?) (Henni checkt, ob sinnvoll) - Docstring da, wo Einsatz sinnvoll, nicht kategorisch überall.
- Final repository **cleanup**

#### Finalize manuscript

[x] Check effects of **fastp and multiqc**, describe in **manuscript** --> Added: fastp is used for quality control and filtering of merged fastq and multiqc generates an interactive html report about the results. Added to manuscripts, including citations.

#### Write documentation

- **document code files in repository** using DocString (Henni)

- **Update README**: Makefile (überarbeitet Lucy), create_db für accession2taxid muss selbst erstellt werden (lässt sich nicht zuverlässig committen) dafür braucht es download, ablage und build Anleitung. (Lucy)

- Write **documentation** for how to **build accessions2taxid database** on your own with **create_taxdb_file.py** and include it in README for setup. It is too large to be provided via repository. Also include testrun with **test.py** from database utils folder (Lucy probiert aus, ob sie das zum Laufen bekommt nach der Anleitung)

### Long-term TODOs:

- Create new datasets and make documented test runs for manuscript

- Finalize manuscript

- Create [CITATION.cff](CITATION.cff)

- Provide pipeline in new clean repository

- Contact all authors for manuscript feedback

- Hand in manuscript (NAR, BMC Bioinformatics or PLOS One)
