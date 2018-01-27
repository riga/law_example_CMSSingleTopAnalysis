#!/usr/bin/env bash

action() {
    local base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && /bin/pwd )"

    # software variables
    export LAW_HOME="$ANALYSIS_BASE/.law"
    export LAW_CONFIG_FILE="$ANALYSIS_BASE/law.cfg"
    export LUIGI_CONFIG_PATH="$ANALYSIS_BASE/luigi.cfg"

    # analysis variables
    export ANALYSIS_BASE="$base"
    export ANALYSIS_LOCAL_STORE="$ANALYSIS_BASE/data"
}
action
