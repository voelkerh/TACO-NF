# Default directory containing .def files and build script
CONTAINER_DIR ?= nextflow/appcontainer

.PHONY: build clean cleanbuild

# Build all containers
buildcontainers:
	./$(CONTAINER_DIR)/build_containers.sh $(CONTAINER_DIR)

# Pull containers from Galaxy
pullcontainers:
	singularity pull nextflow/appcontainer/sra-tools.sif https://depot.galaxyproject.org/singularity/sra-tools%3A3.1.0--h9f5acd7_0
	singularity pull nextflow/appcontainer/bowtie2.sif https://depot.galaxyproject.org/singularity/bowtie2%3A2.5.4--he96a11b_5
	singularity pull nextflow/appcontainer/ganon.sif https://depot.galaxyproject.org/singularity/ganon:2.1.0--py39ha35b9be_0
	singularity pull nextflow/appcontainer/entrez-direct.sif https://depot.galaxyproject.org/singularity/entrez-direct%3A22.1--he881be0_0
	singularity pull nextflow/appcontainer/fastp.sif https://depot.galaxyproject.org/singularity/fastp%3A0.23.4--hadf994f_2
	singularity pull nextflow/appcontainer/multiqc.sif https://depot.galaxyproject.org/singularity/multiqc%3A1.19--pyhdfd78af_0
	singularity pull nextflow/appcontainer/kraken2.sif https://depot.galaxyproject.org/singularity/kraken2%3A2.1.3--pl5321hdcf5f25_0

# Clean all .sif files
cleancontainers:
	./$(CONTAINER_DIR)/build_containers.sh $(CONTAINER_DIR) clean

# Clean and rebuild all containers
cleanbuildcontainers: cleancontainers buildcontainers

