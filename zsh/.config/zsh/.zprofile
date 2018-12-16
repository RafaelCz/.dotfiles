# configure history file
export HISTFILE=$ZDOTDIR/.zhistfile
export HISTSIZE=1000
export SAVEHIST=1000

# set default browser
export BROWSER=/usr/bin/firefox

# disable history file for less
export LESSHISTFILE=-

# default JVM
export JAVA_HOME=/usr/lib/jvm/default-java

# move gnupg-config to a proper location
export GNUPGHOME=$XDG_CONFIG_HOME/gnupg

# move .wgetrc to a proper location
export WGETRC=$XDG_CONFIG_HOME/wget/wgetrc

# move passwordstore-directory to a proper location and enable extensions
export PASSWORD_STORE_DIR=$XDG_DATA_HOME/pass
export PASSWORD_STORE_ENABLE_EXTENSIONS=true

# use fd in fzf
export FZF_DEFAULT_COMMAND="fd --type file --hidden --follow --exclude .git --color=always"
export FZF_DEFAULT_OPTS="--reverse --inline-info --ansi"
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND="fd -t d --color=always"

# move rust stuff to a proper location
export CARGO_HOME=$XDG_DATA_HOME/cargo
export RUSTUP_HOME=$XDG_DATA_HOME/rustup

# move Node.js & NPM to a proper location
export NODE_REPL_HISTORY=$XDG_DATA_HOME/node_repl_history
export NPM_CONFIG_USERCONFIG=$XDG_CONFIG_HOME/npm/npmrc
export NPM_CONFIG_CACHE=$XDG_CACHE_HOME/npm
export NPM_CONFIG_TMP=$XDG_RUNTIME_DIR/npm

# LibSass location
export SASS_LIBSASS_PATH=$HOME/.local/lib

# set (f)path
path=(
	$HOME/.local/bin
	$XDG_DATA_HOME/fzf/bin
	$CARGO_HOME/bin
	$path
)

fpath=(
	$ZDOTDIR/functions
	$fpath
)

# only unique entries, please
typeset -U path fpath

export PATH
