#!/usr/bin/env bash
#
# firewall_rules.sh
# ------------------
# Firewall configuration for Task 3 of the ETTCS801 Integrated Situation.
#
# Goal: the student records server exposes ONE service (SERVICE_PORT) that
#   - must be BLOCKED for the guest network (GUEST_SUBNET)
#   - must be PERMITTED for the authorised staff network (STAFF_SUBNET)
#   - must be BLOCKED for everyone else
#
# >>> REPLACE THE PLACEHOLDERS BELOW with the values given by your assessor
#     for the authorised laboratory network before running this script. <<<

# If your assessor gives you REAL subnets/port for a physical lab network,
# replace the values below with those. As shipped, these values match the
# single-machine simulation in netns_setup.sh (staff_ns / guest_ns / other_ns).
GUEST_SUBNET="192.168.50.0/24"
STAFF_SUBNET="192.168.10.0/24"
SERVICE_PORT="8000"
PROTOCOL="tcp"

set -e

echo "[*] Resetting relevant ufw rules for port ${SERVICE_PORT}/${PROTOCOL} ..."
sudo ufw delete allow "${SERVICE_PORT}/${PROTOCOL}" 2>/dev/null || true

echo "[*] Enabling ufw (if not already active) ..."
sudo ufw --force enable

echo "[*] (3a) Blocking guest network access to the records server ..."
sudo ufw deny from "${GUEST_SUBNET}" to any port "${SERVICE_PORT}" proto "${PROTOCOL}"

echo "[*] (3b) Permitting staff network access to the records server ..."
sudo ufw allow from "${STAFF_SUBNET}" to any port "${SERVICE_PORT}" proto "${PROTOCOL}"

echo "[*] (3c) Blocking all other inbound access to the service ..."
sudo ufw deny "${SERVICE_PORT}/${PROTOCOL}"

echo "[*] Rule order matters in ufw (first match wins), so verify with:"
echo "    sudo ufw status numbered"
echo
echo "Done. Current status:"
sudo ufw status verbose
