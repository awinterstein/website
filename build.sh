#!/bin/bash

# get the directory in which this script is located (the theme source dir)
SOURCE_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

# create blog comments files, if needed
"$SOURCE_DIR/retrieve-comments.py" --create-empty

# create the container for zola builds and tailwindcss updates
docker build -t develop-zola-tailwindcss "${SOURCE_DIR}/themes/project-portfolio" || exit 2

# update the CSS file using tailwindcss
docker run --rm -v ${SOURCE_DIR}:/source:Z -w /source develop-zola-tailwindcss \
    tailwindcss -i themes/project-portfolio/src/css/main.css -o static/css/main.css --minify || exit 3

# build the website via zola
if command -v zola >/dev/null 2>&1; then
    zola build
else
    docker run --rm -v ${SOURCE_DIR}:/source:Z -w /source develop-zola-tailwindcss \
        zola build || exit 3
fi