#!/usr/bin/env bash

action() {
	local base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && /bin/pwd )"
	local parent="$( dirname "$base" )"

	# update variables
	export PYTHONPATH="$base:$PYTHONPATH"

	# source development projects in parent directory
	for p in law order scinum; do
		if [ -d "$parent/$p" ]; then
			if [ -f "$parent/$p/devenv.sh" ]; then
				source "$parent/$p/devenv.sh"
			else
				export PYTHONPATH="$parent/$p:$PYTHONPATH"
			fi
		fi
	done
}
action
