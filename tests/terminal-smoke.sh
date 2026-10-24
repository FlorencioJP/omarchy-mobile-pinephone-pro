#!/bin/bash
# Tests logiciels sur le système ARM64 cible, sans connexion distante.
set -euo pipefail
[[ $EUID != 0 ]] || { echo 'Exécuter sans sudo.' >&2; exit 1; }
socket="omarchy-smoke-$$"
trap 'tmux -L "$socket" kill-server 2>/dev/null || true' EXIT
nvim --headless -u NONE -i NONE -n -c 'lua assert(vim.fn.has("nvim") == 1)' -c qall
tmux -L "$socket" -f /dev/null new-session -d -s omarchy-check 'sleep 30'
[[ $(tmux -L "$socket" display-message -p '#S') == omarchy-check ]]
printf 'omarchy\nother\n' | fzf --filter=omarchy | grep -qx omarchy
printf 'omarchy\n' | rg -qx omarchy
command=$(xdg-terminal-exec --print-cmd --dir=/tmp printf omarchy)
[[ $command == *foot* ]] || { echo "Terminal inattendu : $command" >&2; exit 1; }
printf '%s\n' "$command"
echo 'TERMINAL_SMOKE_OK : Neovim, tmux, fzf, ripgrep et sélection Foot.'
