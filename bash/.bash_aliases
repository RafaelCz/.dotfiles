# some more ls aliases
alias ls='ls -l --color=auto'
alias ll='ls -alF --color=auto'
alias la='ls -A --color=auto'
alias l='ls -CF --color=auto'

alias ssh='autossh'

# globale Suche nach einer Datei
f() {
    find / -name '$@' 2> /dev/null
}

# SSH mit tmus-Sessionverwaltung
s() {
    autossh -t "$@" 'tmux attach || tmux new'
}
