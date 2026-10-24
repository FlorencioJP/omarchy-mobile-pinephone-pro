#!/bin/bash
# SPDX-License-Identifier: MIT
set -euo pipefail
[[ $EUID != 0 ]] || { echo 'Exécuter avec le compte terminal, sans sudo.' >&2; exit 1; }
source_dir=$(cd -- "$(dirname -- "$0")" && pwd)
config="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/shell.json"
[[ -f $config ]] || { echo "Configuration absente : $config" >&2; exit 1; }
[[ -e $config.before-portage ]] || cp -p "$config" "$config.before-portage"
temporary=$(mktemp "$config.XXXXXX")
trap 'rm -f "$temporary"' EXIT
# Conserver la barre et les extensions mobiles, ajouter les panneaux natifs.
jq 'reduce ["omarchy.menu", "omarchy.image-picker", "omarchy.clipboard", "omarchy.emojis", "omarchy.polkit-agent"][] as $id
  (. ; if any(.plugins[]?; .id == $id) then . else .plugins += [{"id": $id}] end)' \
  "$config" > "$temporary"
chmod --reference="$config" "$temporary"
mv "$temporary" "$config"
install -d "$HOME/.local/share/applications"
install -m644 "$source_dir/applications/omarchy-menu.desktop" "$HOME/.local/share/applications/omarchy-menu.desktop"
echo 'Menu Omarchy ajouté ; configuration mobile conservée.'
