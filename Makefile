# Default directory containing .def files and build script
CONTAINER_DIR ?= nextflow/appcontainer

.PHONY: build clean cleanbuild

# Build all containers
buildcontainers:
	./$(CONTAINER_DIR)/build_containers.sh $(CONTAINER_DIR)

# Clean all .sif files
cleancontainers:
	./$(CONTAINER_DIR)/build_containers.sh $(CONTAINER_DIR) clean

# Clean and rebuild all containers
cleanbuildcontainers: cleancontainers buildcontainers

