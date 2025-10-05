#!/bin/bash

# Generate Python code from protobuf files
echo "Generating protobuf files..."

# Generate in shared folder
python -m grpc_tools.protoc \
    -I./shared/proto \
    --python_out=./shared/proto \
    ./shared/proto/*.proto

echo "Done! Generated files in shared/proto/"
