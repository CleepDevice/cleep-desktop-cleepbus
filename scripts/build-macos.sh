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

# clear previous process
rm -rf dist/
rm -rf build/

echo
echo
echo
echo "Installing tooling..."
curl https://sh.rustup.rs -sSf | sh

echo
echo
echo "Installing dependencies..."
echo "--------------------------"
python3 -m pip install -r requirements.txt
checkResult $? 0 "Failed to install python dependencies"

echo
echo
echo "Building application..."
echo "-----------------------"
cp scripts/macos.spec pyinstaller.spec
cp scripts/entitlements.plist entitlements.plist
cp scripts/icon.icns icon.icns
python3 -m PyInstaller --clean --noconfirm --log-level DEBUG pyinstaller.spec
checkResult $? 0 "Failed to build cleepbus application"
which codesign
rm pyinstaller.spec

echo
echo
echo "Getting version..."
echo "------------------"
VERSION=`dist/cleepbus/cleepbus --version`
checkResult $? 0 "Failed to get cleepbus version"
echo $VERSION > dist/version.txt
echo "Found version $VERSION"
echo macos > dist/platform.txt

echo
echo
echo "Generated files"
echo "---------------"
find ./

