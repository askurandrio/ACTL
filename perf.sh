#!/bin/bash


set -xe


time PYTHONPATH=./library python -m cProfile -o $1 $(realpath ./library/actl/run.py) $2 $3

python -m snakeviz $1
