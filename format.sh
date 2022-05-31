#!/bin/bash

set -e

black -S . &> /dev/null

for filename in $(find . -type f -name "*.py"); do
	sed -e 's/    /\t/g' ${filename} > ${filename}-tab
	mv ${filename}-tab $filename
done
