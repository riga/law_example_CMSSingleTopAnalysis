#!/usr/bin/env bash

action() {
    local base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && /bin/pwd )"

    local sw_base="$base/devsoftware"
    echo "installing development software in $sw_base"

    _install_pip() {
        pip install --ignore-installed --prefix "$sw_base" "$1"
    }

    _install_pip luigi
    _install_pip six
    _install_pip scinum
    _install_pip order
    # _install_pip law
    _install_pip git+https://github.com/riga/law.git
}
action "$@"
