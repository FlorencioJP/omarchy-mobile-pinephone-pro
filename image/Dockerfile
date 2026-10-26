# SPDX-License-Identifier: MIT
FROM debian:trixie-slim@sha256:62bd423aeee912639ca8ee681c2b762cb3e25137e0a92b20be455898a9f034ad
# Freeze host utilities as well as the target package transaction.
RUN rm /etc/apt/sources.list.d/debian.sources && \
    printf '%s\n' 'deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/20261026T000000Z/ trixie main' > /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl git gnupg gpgv python3 e2fsprogs fdisk gdisk \
      dosfstools mtools xz-utils zstd jq util-linux shellcheck libarchive-tools && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /src
ENV LC_ALL=C.UTF-8
ENTRYPOINT ["bash"]
