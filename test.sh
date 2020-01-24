#!/bin/bash


set -x

PYTHONPATH=./library py.test ./tests -x
PYTHONPATH=./library pylint actl library tests

