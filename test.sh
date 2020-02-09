#!/bin/bash


set -x
set -e


PYTHONPATH=./library py.test --cov=library --cov-report term-missing --cov-branch --no-cov-on-fail ./tests -x
PYTHONPATH=./library pylint library tests
