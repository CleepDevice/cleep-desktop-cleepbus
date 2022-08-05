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
REPO="tangb/cleep-desktop-cleepbus"
gh config set prompt disabled
checkResult $? 0 "gh binary is not available ?"

echo
echo
echo "Getting version..."
echo "------------------"
VERSION=`cat dist/version.txt | tr -d "\r"`
echo "Found version $VERSION"

echo
echo
echo "Checking existing release..."
echo "----------------------------"
TAG=`echo "v$VERSION"`
gh release view "$TAG" --repo "$REPO" > /dev/null
if [ $? -ne 0 ]
then
    echo "Creating new release $VERSION..."
    gh release create "$TAG" --prerelease --title "$VERSION" --repo "$REPO"
    checkResult $? 0 "Error creating new Github release"
fi

echo
echo
echo "Uploading files..."
echo "------------------"
gh release upload "$TAG" dist/*.zip --repo "$REPO"

