#!/bin/bash
set -euo pipefail
source_dir=$(cd -- "$(dirname -- "$0")/.." && pwd)
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
export HOME="$temporary" XDG_CONFIG_HOME="$temporary/.config"
mkdir -p "$XDG_CONFIG_HOME/omarchy"
config="$XDG_CONFIG_HOME/omarchy/shell.json"
printf '%s\n' '{"version":1,"bar":{"id":"omamobile.bar"},"custom":42,"plugins":[{"id":"omamobile.launcher"},{"id":"omarchy.menu","custom":true}]}' > "$config"
chmod 640 "$config"
cp "$config" "$temporary/original.json"
bash "$source_dir/configure-user.sh"
jq -e '.bar.id == "omamobile.bar" and .custom == 42 and ([.plugins[] | select(.id == "omarchy.menu")] | length) == 1 and any(.plugins[]; .id == "omarchy.menu" and .custom == true) and any(.plugins[]; .id == "omamobile.launcher")' "$config" >/dev/null
cp "$config" "$temporary/first.json"
bash "$source_dir/configure-user.sh"
cmp "$config" "$temporary/first.json"
cmp "$config.before-portage" "$temporary/original.json"
[[ $(stat -c %a "$config") == 640 ]]
[[ -f $HOME/.local/share/applications/omarchy-menu.desktop ]]
echo 'Configuration utilisateur : préservation, idempotence et sauvegarde vérifiées.'
