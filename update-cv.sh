#!/bin/bash

cd cv || exit 1
./templates/create-resume.py -c resume.de.toml -t mteck -p portrait.jpg || exit 2
./templates/create-resume.py -c resume.en.toml -t mteck -p portrait.jpg || exit 3
cp ./build/cv-*.pdf ../static/documents/ || exit 4