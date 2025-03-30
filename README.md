# Comparison of Taxonomic Classification Tools for WGS Data

A customizable nextflow pipeline to compare taxonomic classification tools for whole genome sequencing data.

![Pipeline](./Images/pipeline.png)

---

## Table of Content

* [Installation](#installation)
* [Run the pipeline](#run-the-pipeline)
* [Integrate an additional taxonomic classification tool](#integrate-an-additional-taxonomic-classification-tool)

---

### Installation

Make sure you have [nextflow](https://www.nextflow.io/docs/latest/install.html) and [singularity](https://docs.sylabs.io/guides/latest/admin-guide/installation.html) installed on your Linux system. You may also use [apptainer](https://apptainer.org/docs/admin/main/installation.html) (?).

Clone the repo and cd into the directory:
  ```bash
    git clone https://--.git
    cd --
  ```

Use Makefile to pull singularity containers from galaxy and build additional python containers:
  ```bash
    make buildcontainers
    make pullcontainers
  ```
You can delete or delete and rebuild the containers:
  ```bash
    make cleancontainers
    make cleanbuildcontainers
  ```

You can also build containers manually:
  ```bash
    singularity build python_container.sif python_container.def
    singularity build python_container_plotly.sif  python_container_plotly.def
  ```

In the next step, download the NCBI taxonomy and accession-to-taxid mapping files, then create a local SQLite database required for taxonomy-based conversion in the pipeline.
  ```bash
    cd nextflow/conversion/Database/database_utils
    wget ftp://ftp.ncbi.nih.gov/pub/taxonomy/new_taxdump/new_taxdump.tar.gz
    tar -xzf new_taxdump.tar.gz
    wget ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz
    gunzip nucl_gb.accession2taxid.gz
    python3 create_tax_db_file.py
  ```

Make sure that **database.db** is located in **nextflow/conversion/Database**, not in a subfolder.
You can test the result using the test.py file provided in the database_utils subfolder.

---

### Run the pipeline
(TODO: specifiy user input)

With example file:

```bash
    nextflow run workflow.nf -profile singularity
```

With own accessionFile:

```bash
    nextflow run workflow.nf -$(ownFile.txt)
```

You'll find an [example file here](nextflow/sample_files/pipeline_input/sra_accession.txt)

```txt
# Accession, number of reads, refseq
SRR28741185, 100000, NZ_CP074354
SRR21735255, 2000000, NZ_CP097112
```

---

### Integrate an additional taxonomic classification tool

To integrate an additional taxonomic classification tool for comparison you will need to make adjustments to the pipeline.

- Move to the classification folder and create a subfolder for the tool. Place the classification workflow here.
- If the workflow requires an additional container, add the reference to the Makefile, place the path in the nextflow.config and use the respective parameter in the workflow.
- Include the new classification workflow in the central workflow.nf. Integrate the output in the concatenation of tool_outputs.
- Check, if the file format of the classification output is supported by the converter layer. You find the respective converters in nextflow/conversion/to_kraken_converters/converters/. Currently supported: SAM, kraken2 report format, tre. If the required format is not supported, implement a new converter as a subclass of abstract_converter.py and place it in the converters folder.
