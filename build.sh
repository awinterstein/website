#!/bin/bash

# get the directory in which this script is located (the theme source dir)
SOURCE_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

ZOLA_COMMAND="zola build"

# call the zola executable, if it can be found in the path
if command -v zola >/dev/null; then
    pushd "${SOURCE_DIR}" >/dev/null
    ${ZOLA_COMMAND}
    popd >/dev/null

# alternatively use docker to create and run a container and execute zola from there
elif command -v docker >/dev/null; then

    # create the container for zola builds and tailwindcss updates
    docker build -t develop-zola-tailwindcss "${SOURCE_DIR}/themes/blow" || exit 2

    # update the CSS file using tailwindcss
    docker run --user $UID:$(id -g) --mount type=bind,source=${SOURCE_DIR},target=/source -w /source develop-zola-tailwindcss \
        ${ZOLA_COMMAND} || exit 3

# print an error message if neither tailwindcss nor the docker executable could be found
else
    echo "Need either 'tailwindcss' or 'docker' executable in the path." >&2
    exit 1
fi
