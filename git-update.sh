#!/bin/bash

# Check for optional --build flag
BUILD_SITE=false
if [ "$1" == "--build" ]; then
    BUILD_SITE=true
fi

# Conditionally run Hugo
if [ "$BUILD_SITE" = true ]; then
    if hugo; then
        echo "✅ Hugo site build complete."
    else
        echo "❌ Hugo build failed. Aborting git push."
        exit 1
    fi
fi

# Run notebook conversion and check if it succeeded
if ./content/post/convert_notebooks.sh; then
    echo "✅ Notebook conversion complete."
else
    echo "❌ Notebook conversion failed. Aborting git push."
    exit 1
fi

echo "What is the commit message?"
read message

git add . && git commit -am "$message" && git push

