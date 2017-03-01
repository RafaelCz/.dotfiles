" Show the cursor position
set ruler

" Enable line numbers
set number

" Enable syntax highlighting
syntax on

" Set color sheme
color smyck

" Set dark background
set background=dark

" Highlight current line
set cursorline

" Make tabs as wide as two spaces
set tabstop=2

" Allow cursor keys in insert mode
set esckeys

" Allow backspace in insert mode
set backspace=indent,eol,start

" Optimize for fast terminal connections
set ttyfast

" Use UTF-8 without BOM
set encoding=utf-8 nobomb

" Don’t add empty newlines at the end of files
set binary
set noeol

" Highlight searches
set hlsearch

" Highlight dynamically as pattern is typed
set incsearch

" Smart case-insensitive, incremental search
set ignorecase
set smartcase

" Always show status line
set laststatus=2

" Show the current mode
set showmode

" Show the filename in the window titlebar
set title

" Show the (partial) command as it’s being typed
set showcmd

" Enable mouse in all modes
set mouse=a

" gVim specific settings
" Remove the toolbar and menubar
set guioptions-=T 
set guioptions-=m

" Remove right- and left-hand scrollbars
set guioptions-=r    
set guioptions-=L

" Console-based dialogs for simple queries
set guioptions+=c

