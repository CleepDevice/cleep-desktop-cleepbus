#!/bin/bash

# Check command result
# $1: command result (usually $?)
# $2: awaited command result
# $3: error message
checkResult() {
    if [ $1 -ne $2 ]
    then
        msg=$3
        if [[ -z "$1" ]]; then
            msg="see output log"
        fi
        echo -e "Error occured: $msg."
        exit 1
    fi
}

# env
VERSION=`cat dist/version.txt | tr -d "\r" | xargs`
PLATFORM=`cat dist/platform.txt | tr -d "\r" | xargs`
ARCHIVE="cleepbus-v$VERSION-$PLATFORM-x64.zip"
mkdir package

echo
echo
echo "Packaging application..."
echo "------------------------"
cd dist/cleepbus
zip -q -8 -r "../../package/$ARCHIVE" .
checkResult $? 0 "Failed to package application"
echo "Package $ARCHIVE built successfully"

echo
echo
echo "Generated files"
echo "---------------"
cd ../../package
ls -l

