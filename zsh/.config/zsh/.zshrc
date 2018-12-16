# zsh options
setopt AUTOCD
setopt EXTENDED_GLOB
setopt MENU_COMPLETE

setopt APPENDHISTORY
setopt INC_APPEND_HISTORY SHARE_HISTORY
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_IGNORE_SPACE
setopt HIST_REDUCE_BLANKS

unsetopt BEEP

# use emacs keybindings
bindkey -e

# enable autocompletition
zstyle :compinstall filename '/home/rafael/.config/zsh/.zshrc'

# case-insensitive (all) completion
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'

autoload -Uz compinit
compinit

# set personal aliases & functions
source $ZDOTDIR/.zaliases
source $ZDOTDIR/.zfunctions

# load fzf
[[ $- == *i* ]] && source $XDG_DATA_HOME/fzf/shell/completion.zsh 2> /dev/null
source $XDG_DATA_HOME/fzf/shell/key-bindings.zsh

# enable popup notifications in Pantheon-Terminal
builtin . /usr/share/io.elementary.terminal/enable-zsh-completion-notifications || builtin true

# load pure prompt
PURE_PROMPT_SYMBOL='»'
autoload -U promptinit; promptinit
prompt pure
