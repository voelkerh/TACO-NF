#!/bin/bash

# Get directory path from first argument
CONTAINER_DIR=${1:?Error: Container directory not specified}
COMMAND=${2:-build}  # Default command is build

# Check if directory exists
if [ ! -d "$CONTAINER_DIR" ]; then
    echo "Error: Directory '$CONTAINER_DIR' does not exist"
    exit 1
fi

# Check if singularity is installed
if ! command -v singularity &> /dev/null; then
    echo "Error: Singularity is not installed"
    exit 1
fi

# Clean function
clean_containers() {
    echo "Cleaning .sif files in $CONTAINER_DIR"
    find "$CONTAINER_DIR" -name "*.sif" -delete
    echo "Cleanup complete"
}

# Build function
build_containers() {
    echo "Looking for .def files in $CONTAINER_DIR"
    DEF_FILES=$(find "$CONTAINER_DIR" -name "*.def")

    if [ -z "$DEF_FILES" ]; then
        echo "No .def files found in $CONTAINER_DIR"
        exit 0
    fi

    # Build each container
    for def_file in $DEF_FILES; do
        sif_file="${def_file%.def}.sif"
        echo "Building $sif_file from $def_file..."
        
        if sudo singularity build "$sif_file" "$def_file"; then
            echo "Successfully built $sif_file"
        else
            echo "Failed to build $sif_file"
            exit 1
        fi
    done

    echo "Build process complete"
}

# Execute command based on input
case "$COMMAND" in
    "clean")
        clean_containers
        ;;
    "build")
        build_containers
        ;;
    *)
        echo "Error: Unknown command '$COMMAND'"
        exit 1
        ;;
esac