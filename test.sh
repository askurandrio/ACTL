#!/bin/bash


set -x
set -e


PYTHONPATH=./library py.test --cov=library --cov-report term-missing --cov-branch --no-cov-on-fail ./tests -x --cov-fail-under 93 -vv
python3 -m coverage_badge -f -o coverage.svg
PYTHONPATH=./library pylint library tests
