# Default directory containing .def files and build script
CONTAINER_DIR ?= nextflow/appcontainer

.PHONY: build clean cleanbuild

# Build all containers
build:
	./$(CONTAINER_DIR)/build_containers.sh $(CONTAINER_DIR)

# Clean all .sif files
clean:
	./$(CONTAINER_DIR)/build_containers.sh $(CONTAINER_DIR) clean

# Clean and rebuild all containers
cleanbuild: clean build

