#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

for D in *; do
	if [ -d "${D}" ]; then
		echo "${D}: " && stow "${D}" 2> /dev/null && echo "linked" || echo "failed"
	fi
done
