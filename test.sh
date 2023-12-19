#!/bin/bash


set -xe


if [[ "$1" == "format" ]]; then
    ./format.sh
    exit 0
elif [[ "$1" == "pytest" ]]; then
    PYTHONPATH=./library python -m pytest --cov=library --cov-report term-missing --cov-branch --no-cov-on-fail ./tests -x --cov-fail-under 93 -vv
elif [[ "$1" == "-k" ]]; then
    PYTHONPATH=./library python -m pytest ./tests -x -k $2 -vv
elif [[ "$1" == "pylint" ]]; then
    PYTHONPATH=./library python -m pylint library tests
else
    ./test.sh format
    ./test.sh pytest
    python -m coverage_badge -f -o coverage.svg
    ./test.sh pylint
fi
