#!/bin/bash


set -x
set -e


PYTHONPATH=./library py.test --cov=library --cov-report term-missing ./tests -x
PYTHONPATH=./library pylint library tests
