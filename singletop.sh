#!/usr/bin/env bash

action() {
	local base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && /bin/pwd )"

	# analysis variables
	export ANALYSIS_BASE="$base"
	export ANALYSIS_LOCAL_STORE="$ANALYSIS_BASE/data"
	export LAW_CONFIG_FILE="$ANALYSIS_BASE/law.cfg"
	export LUIGI_CONFIG_PATH="$ANALYSIS_BASE/luigi.cfg"
}
action
