#!/usr/bin/env bash
#
# netns_teardown.sh
# ------------------
# Removes the namespaces and veth pairs created by netns_setup.sh.
# Safe to run even if some of them don't exist.

sudo ip netns delete staff_ns 2>/dev/null || true
sudo ip netns delete guest_ns 2>/dev/null || true
sudo ip netns delete other_ns 2>/dev/null || true

# Deleting a namespace also removes the veth end that was inside it;
# the host-side end sometimes lingers, so clean it up explicitly too.
sudo ip link delete veth-staff-br 2>/dev/null || true
sudo ip link delete veth-guest-br 2>/dev/null || true
sudo ip link delete veth-other-br 2>/dev/null || true

echo "[OK] Namespaces and veth pairs removed."
