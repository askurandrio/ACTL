#!/bin/bash


set -x
set -e

./format.sh
PYTHONPATH=./library python -m pytest --cov=library --cov-report term-missing --cov-branch --no-cov-on-fail ./tests -x --cov-fail-under 94 -vv
python -m coverage_badge -f -o coverage.svg
PYTHONPATH=./library python -m pylint library tests
