# Risk Assessment — ULK Polytechnic Institute Student Records System

## 1a. Assets, Vulnerabilities and Consequences

| # | Asset | Vulnerability | Possible Consequence |
|---|-------|----------------|------------------------|
| 1 | Central student records server | Guest network has access to the records server | An unauthorised or compromised guest device could read, copy, or tamper with student records; the repeated connection attempts from an unfamiliar external address suggest this exposure is already being probed. |
| 2 | Staff accounts / authentication system | Weak staff passwords | An attacker who guesses or brute-forces a staff password gains legitimate-looking access to the records server, bypassing perimeter controls entirely. |
| 3 | Inter-campus file transfer channel | Files are transferred between campuses unencrypted, and server software is outdated | Student data in transit can be intercepted and read (or altered) by anyone on the path between campuses; outdated software on the server may also contain known, unpatched vulnerabilities that let an attacker gain deeper access once on the network. |

## 1b. Risk Ranking (Likelihood × Impact)

| Rank | Risk | Likelihood | Impact | Reasoning |
|------|------|-----------|--------|-----------|
| 1 (Highest) | Guest network access to the records server | High | High | The scenario already reports repeated connection attempts from an unfamiliar external address — this is not theoretical, it is an active, observed threat with a direct path to the asset. |
| 2 | Weak staff passwords | High | High | Weak passwords are common and easy to exploit (guessing, credential stuffing, phishing), and a compromised staff account gives an attacker trusted-level access to the records server. |
| 3 | Unencrypted file transfers + outdated software | Medium | Medium–High | Interception requires the attacker to be positioned on the transfer path, which is a somewhat higher bar than the two risks above, but outdated software raises the impact if the attacker does gain a foothold, since known exploits may be readily available. |

## 1c. Recommended Controls

| Risk | Recommended Control |
|------|----------------------|
| Guest network access to the records server | Network segmentation: place the records server on a restricted VLAN/subnet and use firewall rules (see `firewall/`) to deny all guest-network traffic to it by default, permitting only the authorised staff subnet. |
| Weak staff passwords | Enforce a strong password policy (minimum length/complexity, no reuse) combined with multi-factor authentication (MFA) for any account that can reach the records server. |
| Unencrypted file transfers / outdated software | Replace plaintext transfer methods with an encrypted channel (e.g. SFTP/SCP or TLS) for inter-campus transfers, and establish a regular patch-management schedule for server software. |

---
*Note: This assessment is based on the scenario described in the ETTCS801 Integrated Situation brief. No real student records or credentials were used or stored while preparing this document.*
