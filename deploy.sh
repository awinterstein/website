#!/bin/bash

# get the directory in which this script is located (the theme source dir)
SOURCE_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

# build the website first
"$SOURCE_DIR/build.sh"

# sync the files to the web hosting
rsync -r --delete public/ ngcobalt447.manitu.net:/home/sites/site100040730/web/winterstein.biz/
