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

	# source dev software
	export LAW_DEV_SOFTWARE="$base/devsoftware"
	if [ -d "$LAW_DEV_SOFTWARE" ]; then
		# luigi
		_addpy "$LAW_DEV_SOFTWARE/luigi"
		_addbin "$LAW_DEV_SOFTWARE/luigi/bin"

		# six
		_addpy "$LAW_DEV_SOFTWARE/six"

		# law
		_addpy "$LAW_DEV_SOFTWARE/law"
		_addbin "$LAW_DEV_SOFTWARE/law/bin"
		source "$( law completion )"

		# order
		_addpy "$LAW_DEV_SOFTWARE/order"
	fi

	# add _this_ repo
	_addpy "$base"
}
action "$@"
