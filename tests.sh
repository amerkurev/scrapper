#!/bin/bash

PYTHONPATH=$(pwd)/app coverage run --source=app/ -m pytest app/
coverage report -m

# if pass `coveralls` as argument, then send coverage report to coveralls.io
if [ "$1" == "coveralls" ]; then
    coveralls --service=github
fi
# if pass `html` as argument, then generate html report
if [ "$1" == "html" ]; then
    coverage html
fi
