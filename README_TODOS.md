# To Dos

### Kurzfristige TODOS:

#### 1. Restructure modules to match architecture in manuscript - Done

#### 2. Rename variables - Done

#### 3. Restructure Workflows - Done

#### 4. Update container definitions and makefile - Done

### Further TODOs:

- Check **refseq in pipeline input**:
    --> !! refseq is required information for bowtie2. These are accession numbers for reference sequences for organisms provided by NCBI in the RefSeq Database (other than SRA Database). bowtie2.nf extracts these (! 1st row commentary needed / will be cut off) and downloads refseqs for specific organisms to map the reads to.
  - Decide: New process to find suitable refseq for sra accession or **change requirements in manuscript**!

- Check effects of **fastp and multiqc**, describe in **manuscript**

- Integrate **ganon**:
  - Find out about ganon database file
  - Translate ganon comments into English, transfer to tools integration documentation in README.md

- Bowtie2: **bowtie2.nf** has a process, which **merges fastq** input files -> Currently we have a combined fastq from the preparation module as input, is this redundant?

- Identify reasons for visualization issues:
  - Tree representation has artefacts -> merged_newick_tree.txt probably has issues, possibly due to conversion from kraken
  - Check order of tree and heatmap for consistency

- Write **test suite** with pytest workflow

- Write **documentation** for how to **build accessions2taxid database** on your own with **create_taxdb_file.py** and include it in README for setup. It is too large to be provided via repository. Also include testrun with **test.py** from database utils folder

- Use **PEP-8** formatting for **all python files**, possibly use linter

- Find out about formatting **conventions** for nextflow files and **harmonize all workflow files**

- Find out about **useful and popular documentation pracitces** for workflows and files, **document code files in repository**

- **Update README**: Makefile, create_db für accession2taxid muss selbst erstellt werden (lässt sich nicht zuverlässig committen) dafür braucht es download, ablage und build Anleitung

- Final repository **cleanup**

### Long-term TODOs:

- Create new datasets and make documented test runs for manuscript

- Finalize manuscript

- Create [CITATION.cff](CITATION.cff))

- Provide pipeline in new clean repository

- Contact all authors for manuscript feedback

- Hand in manuscript (NAR, BMC Bioinformatics or PLOS One)
