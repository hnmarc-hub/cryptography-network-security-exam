# Firewall Filter Tests — Task 3d

This uses the single-machine network-namespace simulation from `netns_setup.sh`
(three fake networks: `staff_ns` 192.168.10.0/24, `guest_ns` 192.168.50.0/24,
`other_ns` 10.99.99.0/24), since only one physical machine was available.
If you were given a real multi-host lab network instead, replace the IPs
below with the real ones and skip the netns setup.

## Setup (run once)

```bash
cd firewall
chmod +x netns_setup.sh netns_teardown.sh firewall_rules.sh
./netns_setup.sh

# Apply the firewall rules
./firewall_rules.sh
sudo ufw status numbered

# Start the "records server" on the host, listening on all interfaces
python3 -m http.server 8000 --bind 0.0.0.0
# (leave this running in its own terminal tab for the tests below)
```

## Test 1 — Permitted connection (staff network)

| Field | Value |
|---|---|
| Command | `sudo ip netns exec staff_ns curl --max-time 3 -s -o /dev/null -w "HTTP %{http_code}\n" http://192.168.10.1:8000/` |
| Expected outcome | Connection succeeds — prints `HTTP 200` (allowed by rule 3b) |
| Actual result | *[paste terminal output here]* |

## Test 2 — Blocked connection (guest network)

| Field | Value |
|---|---|
| Command | `sudo ip netns exec guest_ns curl --max-time 3 -s -o /dev/null -w "HTTP %{http_code}\n" http://192.168.50.1:8000/` |
| Expected outcome | Times out / connection refused, no HTTP response (blocked by rule 3a) |
| Actual result | *[paste terminal output here]* |

## Test 3 — Blocked connection (other/external network)

| Field | Value |
|---|---|
| Command | `sudo ip netns exec other_ns curl --max-time 3 -s -o /dev/null -w "HTTP %{http_code}\n" http://10.99.99.1:8000/` |
| Expected outcome | Times out / connection refused (blocked by the default-deny rule 3c) |
| Actual result | *[paste terminal output here]* |

## Cleanup

```bash
./netns_teardown.sh
```

## Note

Each fake network reaches the host directly over its own virtual link, so
`ufw`'s source-subnet matching on the host applies exactly as it would to
real staff/guest/other hosts on physical interfaces — this is a faithful
test of the firewall logic, just without needing three physical machines.

---

## Recorded Results (executed 28 Sep 2026, WSL Ubuntu)

Firewall rules in force (sudo ufw status numbered):

    [ 1] 8000/tcp                   DENY IN     192.168.50.0/24
    [ 2] 8000/tcp                   ALLOW IN    192.168.10.0/24
    [ 3] 8000/tcp                   DENY IN     Anywhere
    [ 4] 8000/tcp (v6)              DENY IN     Anywhere (v6)

| Test | Source | Expected | Actual result | Pass? |
|---|---|---|---|---|
| 1 Permitted | staff_ns 192.168.10.2 | HTTP 200 | HTTP 200, curl exit code 0 | Yes |
| 2 Blocked | guest_ns 192.168.50.2 | Timeout, no response | HTTP 000, curl exit code 28 (timeout) | Yes |
| 3 Blocked | other_ns 10.99.99.2 | Timeout, no response | HTTP 000, curl exit code 28 (timeout) | Yes |

Server log during the tests showed only one request, from the staff address:

    192.168.10.2 - - [28/Sep/2026 14:41:41] "GET / HTTP/1.1" 200 -

The guest and other requests never reached the server, confirming the firewall dropped them.
