#!/bin/bash
if [ "$1" -eq "" ]
then
    BRANCH=master
    echo "BRANCH not specified ... defaulting to master"
else
    BRANCH=$1
fi
git fetch --all
git reset --hard origin/$BRANCH
