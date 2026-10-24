# Contributing

This is an experimental integration tested on one PinePhone Pro. Start with the current validation matrix in the README; do not assume a working UI proves working charging, suspend, radios or storage migration.

For a hardware report, include the phone edition, whether the official keyboard is mounted, kernel/Omarchy/Hyprland versions, SD versus eMMC root, exact reproduction steps and observed results. State separately what was configured, compiled, run and tested on hardware.

Attach only relevant portions of logs. Remove passwords, SSH material, personal file paths, Wi-Fi credentials, identifiers and remote machine addresses. Never submit a used system image containing account or network secrets.

Keep patches small and retain the PinePhone Pro kernel, drivers and existing boot chain unless an explicit, separately reviewed change is required. Do not copy Pixel fastboot or partitioning procedures. Never silently substitute another desktop for Omarchy Mobile.

Run the focused checks listed in the README. Changes to live UI behavior also need a device test or a clearly labelled untested status; host CI is not a hardware test. When changing package inputs, include exact versions, architecture, SHA-256, signatures and declared licences, and review package scriptlets and hooks before installation.

This repository publishes source and integration inputs, not a supported bootable distribution. Improvements to a reproducible, secret-free base-image build are welcome, but must not claim an independently reproduced result until that build has actually run.
