#!/bin/bash


set -x
set -e


PYTHONPATH=./library python3.7 -m cProfile -o $1 $(realpath ./library/actl/run.py) $2 $3

python3.7 -m snakeviz $1
