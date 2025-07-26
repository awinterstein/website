#!/bin/bash -e

cd cv
./templates/create-resume.py -c resume.de.toml -t mteck -p portrait.jpg
./templates/create-resume.py -c resume.en.toml -t mteck -p portrait.jpg
cp ./build/cv-*.pdf ../static/documents/

DOCUMENTS_DIR="$HOME/Verteilte Daten/Selbständigkeit"
if [ -d "$DOCUMENTS_DIR" ]; then
    cp ./build/cv-*.pdf "$DOCUMENTS_DIR"
fi
