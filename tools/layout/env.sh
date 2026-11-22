#!/bin/bash
# Re-bind the KiCad 9.0.8 chroot's folders after the container pauses (the bind mounts drop; layout-plan §3.2).
#   /work = this repo, /cap = capture and build scratch, /lab = the layout lab; plus proc, dev and sys.
# Idempotent: a mount already in place is left alone. If /opt/resolute itself is gone, rebuild it first
# (Ubuntu 26.04 debootstrap, then KiCad 9.0.8 and the Python packages in burrito-execution-brief.md).
set -e
ROOT=/opt/resolute
REPO=$(cd "$(dirname "$0")/../.." && pwd)
bind() { mountpoint -q "$ROOT/$2" || mount "${3:---bind}" "$1" "$ROOT/$2"; }
mkdir -p /home/claude/capture /home/claude/layout-lab
bind "$REPO" work
bind /home/claude/capture cap
bind /home/claude/layout-lab lab
mountpoint -q "$ROOT/proc" || mount -t proc proc "$ROOT/proc"
bind /dev dev --rbind
bind /sys sys --rbind
chroot "$ROOT" env HOME=/root kicad-cli version
