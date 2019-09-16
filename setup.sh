#!/usr/bin/env bash

action() {
    #
    # local variables
    #

    if [ ! -z "$ZSH_VERSION" ]; then
        local this_file="${(%):-%x}"
    else
        local this_file="${BASH_SOURCE[0]}"
    fi
    local base="$( cd "$( dirname "$this_file" )" && pwd )"

    local vpython="$( python -c "import sys; print('{0.major}.{0.minor}'.format(sys.version_info))" )"


    #
    # global variables
    #

    export ANALYSIS_BASE="$base"
    export ANALYSIS_STORE="$ANALYSIS_BASE/tmp/data"
    export ANALYSIS_SOFTWARE="$ANALYSIS_BASE/tmp/software"

    export PATH="$ANALYSIS_SOFTWARE/bin:$PATH"
    export PYTHONPATH="$base:$ANALYSIS_SOFTWARE/lib/python${vpython}/site-packages:$PYTHONPATH"


    #
    # helpers
    #

    _install_pip() {
        pip install --ignore-installed --prefix "$ANALYSIS_SOFTWARE" "$@"
    }

    if [ ! -d "$ANALYSIS_SOFTWARE" ]; then
        echo "installing development software in $ANALYSIS_SOFTWARE"
        _install_pip luigi
        _install_pip six
        _install_pip scinum
        _install_pip order
        _install_pip git+https://github.com/riga/law.git
    fi


    #
    # setup law
    #

    export LAW_HOME="$ANALYSIS_BASE/tmp/.law"
    export LAW_CONFIG_FILE="$ANALYSIS_BASE/law.cfg"

    source "$( law completion )"
    law index --verbose
}
action "$@"
