#!/bin/bash


set -x

PYTHONPATH=./library py.test ./tests -x

