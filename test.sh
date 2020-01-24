#!/bin/bash


set -x
set -e


PYTHONPATH=./library py.test ./tests -x
PYTHONPATH=./library pylint actl library tests

