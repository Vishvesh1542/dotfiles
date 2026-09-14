if status is-interactive
    # Commands to run in interactive sessions can go here
    set -g fish_greeting "" # Suppress default welcome message
end

function cd
    builtin cd $argv
    and eza --icons
end

# Environment variables
set -gx EDITOR nvim
set -gx TERMINAL alacritty
fish_add_path ~/.local/share/archy/bin

# Useful Aliases / Abbreviations
abbr -a ls 'eza --icons'       # Modern replacement for ls (if eza/lsd is installed)
abbr -a ll 'eza -l --icons'
abbr -a g 'git'
abbr -a gs 'git status'
abbr -a clear 'clear; printf "\e[3J"' # Clean clear
abbr -a archy-new 'cd $HOME/.local/share/archy/bin/new-install'
abbr -a archy-bin 'cd $HOME/.local/share/archy/bin/'

