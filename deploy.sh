#!/bin/bash

# get the directory in which this script is located (the theme source dir)
SOURCE_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

# build the website first
"$SOURCE_DIR/build.sh"

# import the FTP configuration (the file must include HOST, USER and PASS variables)
# shellcheck source=/dev/null
source "$SOURCE_DIR/.ftp-config"

# define local and remote directories
LCD="$SOURCE_DIR/public"
RCD="/winterstein.biz"

lftp -f "
open $HOST
user $USER $PASS
lcd $LCD
mirror --continue --reverse --delete --verbose $LCD $RCD
bye
"
