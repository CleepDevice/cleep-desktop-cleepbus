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
rm -rf venv/

echo
echo
echo
echo "Installing tooling..."
echo "---------------------"
python3 --version

echo
echo
echo "Preparing venv..."
echo "-----------------"
python3 -m venv venv
source venv/bin/activate

echo
echo
echo "Installing dependencies..."
echo "--------------------------"
python3 -m pip install cython
# workaround for pyzmq install isue with python3.11 and missing longintrepr.h
# -- start
python3 -m pip download pyzmq
tar -xzf pyzmq*
cd pyzmq*
python setup.py clean --all
python setup.py cython
# -- end
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
checkResult $? 0 "Failed to get cleepbus version"
echo $VERSION > dist/version.txt
echo "Found version $VERSION"
echo linux > dist/platform.txt

echo
echo
echo "Generated files"
echo "---------------"
find

deactivate
