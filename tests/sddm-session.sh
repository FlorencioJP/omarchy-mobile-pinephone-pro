#!/bin/bash
# Charger le vrai modèle SDDM sans authentification, affichage ou saisie.
set -euo pipefail
source_dir=$(cd -- "$(dirname -- "$0")/.." && pwd)
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
ln -s "$source_dir/tests" "$temporary/tests"
ln -s "$source_dir/overlay" "$temporary/overlay"
cp "$source_dir/tests/sddm-test.metadata.desktop" "$temporary/metadata.desktop"
status=0
LANG=C.UTF-8 QT_FORCE_STDERR_LOGGING=1 QT_QPA_PLATFORM=offscreen \
  QT_QUICK_BACKEND=rhi QSG_RHI_BACKEND=null timeout 3 sddm-greeter-qt6 \
  --test-mode --theme "$temporary" > "$temporary/result.log" 2>&1 || status=$?
[[ $status == 0 || $status == 124 ]] || { cat "$temporary/result.log"; exit 1; }
grep -Fq 'SDDM_SESSION_OK' "$temporary/result.log" || { cat "$temporary/result.log"; exit 1; }
grep -F 'SDDM_SESSION_' "$temporary/result.log"
! grep -Fq 'SDDM_SESSION_FAILED' "$temporary/result.log"
