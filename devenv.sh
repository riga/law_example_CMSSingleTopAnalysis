#!/usr/bin/env bash

action() {
    local base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && /bin/pwd )"
    local parent="$( dirname "$base" )"

    _addpy() {
        [ ! -z "$1" ] && export PYTHONPATH="$1:$PYTHONPATH"
    }

    _addbin() {
        [ ! -z "$1" ] && export PATH="$1:$PATH"
    }

    # check dev software
    export LAW_DEV_SOFTWARE="$base/devsoftware"
    if [ ! -d "$LAW_DEV_SOFTWARE" ]; then
        echo "please run ./devinstall.sh run install required python packages"
        return
    else
        _addbin "$LAW_DEV_SOFTWARE/bin"
        _addpy "$LAW_DEV_SOFTWARE/lib/$( python -c 'import sys; print("python{}.{}".format(*sys.version_info[0:2]))' )/site-packages"
    fi

    # add _this_ repo
    _addpy "$base"

    # source the law auto-completion script
    source "$( law completion )"
}
action "$@"
