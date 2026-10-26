#!/bin/bash
# SPDX-License-Identifier: MIT
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
mode=${1:-}
[[ $# == 1 && ( $mode == prepare || $mode == resolve || $mode == build || $mode == verify ) ]] || {
  echo 'Usage: bash image/build.sh prepare|build|verify|resolve' >&2; exit 2;
}
tag=omarchy-ppp-image-builder:20261026
if [[ $mode == prepare || $mode == resolve ]]; then
  python3 image/fetch.py
  docker build --platform linux/arm64 -t "$tag" -f image/Dockerfile image
fi
docker image inspect "$tag" >/dev/null
mkdir -p cache/image image/work image/out
if [[ $mode == verify || $mode == prepare ]]; then
  exec docker run --rm --network none -v "$PWD:/src:ro" "$tag" -c 'python3 image/verify.py'
fi
network=none
if [[ $mode == resolve ]]; then network=bridge; mode=prepare; fi
# No physical block device is passed to the builder. Only its own file is mounted.
exec docker run --rm --platform linux/arm64 --privileged --network "$network" \
  -v "$PWD:/src:ro" -v "$PWD/cache/image:/src/cache/image" \
  -v "$PWD/image/work:/src/image/work" -v "$PWD/image/out:/src/image/out" \
  "$tag" /src/image/container.sh "$mode"
