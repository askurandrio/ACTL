#!/bin/bash

set -e

black -S . &> /dev/null || (set -ex; black -S .; exit 1)

for filename in $(find . -type f -name "*.py" -o -name "*.a"); do
	sed -e 's/    /\t/g' ${filename} > ${filename}-tab
	mv ${filename}-tab $filename
done
