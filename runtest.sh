#!/bin/bash

# run pytest with coverage and check the exit code of pytest
if ! PYTHONPATH=$(pwd)/app coverage run --rcfile=.coveragerc -m pytest app/;
then
    echo "Tests failed"
    exit 1
fi

coverage report -m
