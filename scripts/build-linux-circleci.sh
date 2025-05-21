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
echo "Installing tooling..."
echo "---------------------"
sudo apt-get update
sudo apt-get install python3 python3-distutils python3-dev gcc g++ make
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
python3 --version
python3 -m pip --version

echo
echo
echo "Installing dependencies..."
echo "--------------------------"
python3 -m pip install -r requirements.txt
checkResult $? 0 "Failed to install python dependencies"

echo
echo
echo "Packaging application..."
echo "------------------------"
cp scripts/linux.spec pyinstaller.spec
python3 -m PyInstaller --clean --noconfirm --log-level INFO pyinstaller.spec
checkResult $? 0 "Failed to build cleepbus application"
rm pyinstaller.spec

echo
echo
echo "Run application..."
echo "------------------"
dist/cleepbus/cleepbus --debug --test
checkResult $? 0 "Failed to run application"

echo
echo
echo "Getting version..."
echo "------------------"
VERSION=`dist/cleepbus/cleepbus --version`
echo $VERSION > dist/version.txt
echo "Found version $VERSION"
echo linux > dist/platform.txt

echo
echo
echo "Generated files"
echo "---------------"
find

