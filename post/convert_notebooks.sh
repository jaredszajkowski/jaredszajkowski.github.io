#!/bin/bash

VERBOSE=false

# Check for optional --verbose flag
if [ "$1" == "--verbose" ]; then
    VERBOSE=true
fi

for dir in */ ; do
    dirname="${dir%/}"
    notebook_path="${dir}${dirname}.ipynb"

    if [ -f "$notebook_path" ]; then
        echo "Converting $notebook_path"
        python convert_notebook.py "$notebook_path"
    elif [ "$VERBOSE" = true ]; then
        echo "Skipping $dir (notebook not found)"
    fi
done

