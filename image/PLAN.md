<!-- SPDX-License-Identifier: MIT -->
# Reproducible PinePhone Pro microSD image

This work starts from public integration commit
`0afd6bf3e515573f79b699d0a80ed7bbdd678fbf`. The existing installation and the
uncommitted login/keyboard-power experiments are not build inputs.

1. Freeze the official PinePhone Pro barebone image, Omarchy Mobile sources,
   public signing keys and complete package transaction. Verify hashes and
   signatures; retain the package scriptlets/hooks for review.
2. Build only a regular image file. Preserve DanctNIX boot support; never
   expose a physical SD/eMMC target or use fastboot. Run offline from the locked
   package cache after preparation. Record the complete installed inventory.
3. Package the existing PinePhone profile, keyboard map, login and terminal
   helpers with explicit dependencies and installation tests. Provide password
   creation on the device, including the keyboard-free case, without distributing
   account secrets or enabling remote login before provisioning.
4. Check filesystems, boot references, kernel/module pairing, package integrity,
   Hyprland configuration, the input profile and the absence of secrets. Rebuild
   from clean inputs and compare package/file manifests. Byte-identical ext4
   images are not promised.
5. Offer a short microSD hardware protocol and record actual results separately.
   An upstream package contribution remains experimental until that protocol
   passes; the existing documentation PR is kept separate.

Current status: input recovery and build implementation in progress. No new
boot, graphics, input, radio, charge or suspend result is claimed.
