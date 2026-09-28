#!/usr/bin/env bash
#
# netns_setup.sh
# ---------------
# Simulates three separate networks (staff / guest / other) on a single
# machine using Linux network namespaces + veth pairs, so that firewall
# rules can be tested with genuinely different source IP addresses even
# though there is only one physical machine (e.g. a laptop running WSL2).
#
# Run this ONCE before testing. Run netns_teardown.sh when you're done.
# Must be run with sudo privileges (it will prompt as needed).

set -e

echo "[*] Creating namespaces: staff_ns, guest_ns, other_ns ..."
sudo ip netns add staff_ns
sudo ip netns add guest_ns
sudo ip netns add other_ns

echo "[*] Creating veth pairs (virtual cables) ..."
sudo ip link add veth-staff type veth peer name veth-staff-br
sudo ip link add veth-guest type veth peer name veth-guest-br
sudo ip link add veth-other type veth peer name veth-other-br

echo "[*] Moving one end of each cable into its namespace ..."
sudo ip link set veth-staff netns staff_ns
sudo ip link set veth-guest netns guest_ns
sudo ip link set veth-other netns other_ns

echo "[*] Assigning IP addresses ..."
# Host side (the "records server" end) -- one IP per fake network
sudo ip addr add 192.168.10.1/24 dev veth-staff-br
sudo ip addr add 192.168.50.1/24 dev veth-guest-br
sudo ip addr add 10.99.99.1/24   dev veth-other-br

# Namespace side (the "client" end)
sudo ip netns exec staff_ns ip addr add 192.168.10.2/24 dev veth-staff
sudo ip netns exec guest_ns ip addr add 192.168.50.2/24 dev veth-guest
sudo ip netns exec other_ns ip addr add 10.99.99.2/24   dev veth-other

echo "[*] Bringing all interfaces up ..."
sudo ip link set veth-staff-br up
sudo ip link set veth-guest-br up
sudo ip link set veth-other-br up

sudo ip netns exec staff_ns ip link set veth-staff up
sudo ip netns exec staff_ns ip link set lo up

sudo ip netns exec guest_ns ip link set veth-guest up
sudo ip netns exec guest_ns ip link set lo up

sudo ip netns exec other_ns ip link set veth-other up
sudo ip netns exec other_ns ip link set lo up

echo "[OK] Setup complete. Verify with: sudo ip netns list"
echo "     Test connectivity with:"
echo "       sudo ip netns exec staff_ns ping -c 2 192.168.10.1"
echo "       sudo ip netns exec guest_ns ping -c 2 192.168.50.1"
echo "       sudo ip netns exec other_ns ping -c 2 10.99.99.1"
