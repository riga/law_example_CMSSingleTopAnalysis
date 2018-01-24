#!/usr/bin/env bash

action() {
	local base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && /bin/pwd )"

	local sw_base="$base/devsoftware"
	echo "installing development software in $sw_base"
	mkdir -p "$sw_base"

	_install_git() {
		local name="$1"
		local url="$2"
		local tag="$3"
		if [ ! -d "$sw_base/$name" ]; then
			( cd "$sw_base" && git clone "$url" )
			if [ "$?" != "0" ]; then
				2>&1 echo "$name checkout failed"
				return "1"
			fi
			if [ ! -z "$tag" ]; then
				( cd "$sw_base/$name" && git checkout "tags/$tag" )
			fi
		else
			echo "skipping $name, already exists"
		fi
	}

	# luigi
	_install_git "luigi" "https://github.com/spotify/luigi.git" "2.7.2" || return "$?"

	# six
	_install_git "six" "https://github.com/benjaminp/six.git" "1.11.0" || return "$?"

	# law
	_install_git "law" "https://github.com/riga/law.git" || return "$?"

	# order
	_install_git "order" "https://github.com/riga/order.git" || return "$?"
}
action "$@"
