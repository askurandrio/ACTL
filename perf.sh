#!/bin/bash


set -xe

[ ! -z "$PY_COMMAND" ] || PY_COMMAND="$(realpath ./library/actl/run.py) $2 $3"
[ ! -z "$PROFILE_FILENAME" ] || PROFILE_FILENAME='/tmp/tmp.perf'


time PYTHONPATH=./library python -m cProfile -o $PROFILE_FILENAME $PY_COMMAND

python -m snakeviz $PROFILE_FILENAME
