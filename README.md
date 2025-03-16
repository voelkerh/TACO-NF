# Comparison of Taxonomic Classification Tools for WGS Data

---

## Table of Content

* [Quick Start](#quick-start)
* [Install Guide](#install-guide)
* [Build Container](#build-container)
    * [With Makefile](#with-makefile)
    * [Without Makefile](#without-makefile)
* [Run the pipeline](#run-the-pipeline)
* [Pipeline Architecture](#pipeline-architecture)

---

### Quick Start
In order to run the pipeline there are some pre-requires need. 

---

### Install Guide
  - [apptainer](https://apptainer.org/docs/admin/main/installation.html) / [singularity](https://docs.sylabs.io/guides/latest/admin-guide/installation.html) 
    - Linux and on MacOS/Windows through VM like Lima and WSL
  - [nextflow](https://www.nextflow.io/docs/latest/install.html) 
    - POSIX-compatible system (Linux, macOS, etc), and on Windows through WSL.

---

### Build Container
#### With Makefile
Build:
  ```bash
    make buildcontainers
  ```
Delete:
  ```bash
    make cleancontainers
  ```
Rebuild:
  ```bash
    make cleanbuildcontainers
  ```

#### Without Makefile:
apptainer:
  ```bash
    apptainer build python_container.sif python_container.def
    apptainer build python_container_plotly.sif  python_container_plotly.def
  ```

singularity:
  ```bash
    singularity build python_container.sif python_container.def
    singularity build python_container_plotly.sif  python_container_plotly.def
  ```

---

### Run the pipeline

With example file:

```bash
    nextflow run workflow.nf -profile singularity
```

With own accessionFile:

```bash
    nextflow run workflow.nf -$(ownFile.txt)
```

You'll find an [example file here](nextflow/preparation/sra_accession.txt)

```txt
# Accession, number of reads, refseq
SRR28741185, 100000, NZ_CP074354
SRR21735255, 2000000, NZ_CP097112
```

---

### Pipeline Architecture

![Pipeline](./Images/pipeline.png)
