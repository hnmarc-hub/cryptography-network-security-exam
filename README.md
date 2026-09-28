# Cryptography & Network Security — Integrated Situation (ETTCS801)

Security toolkit and lab evidence for the ULK Polytechnic Institute student
records scenario: risk assessment, a Python encryption/integrity tool, and
firewall traffic filtering.

## Project structure

```
cryptography-network-security-exam/
├── risk_assessment.md          # Task 1: assets, vulnerabilities, ranking, controls
├── encryption_tool.py          # Task 2: encrypt / decrypt / hash / verify CLI
├── requirements.txt            # Python dependencies
├── sample_data/
│   └── sample_student_record.txt   # dummy sample data ONLY — no real records
├── firewall/
│   ├── firewall_rules.sh       # Task 3: ufw rules (guest deny / staff allow / default deny)
│   └── filter_tests.md         # Task 3d: test commands, expected vs actual results
├── report/
│   └── report.tex              # Task 5: LaTeX technical report (+ compiled report.pdf)
└── .gitignore                  # excludes keys and real data from the repo
```

## Prerequisites

- Python 3.10+
- `pip install -r requirements.txt`
- A Linux environment with `ufw` for the firewall section (tested on Ubuntu/WSL2)

## 1. Setup

```bash
git clone <your-repo-url>
cd cryptography-network-security-exam
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Encryption toolkit usage

The encryption key is **never stored inside the repository**. By default the
tool writes/reads it at `../secret.key` (i.e. one directory above the repo);
you can point `--key` anywhere else you prefer.

```bash
# Generate a key (do this once)
python3 encryption_tool.py genkey --key ../secret.key

# Encrypt the sample record
python3 encryption_tool.py encrypt sample_data/sample_student_record.txt \
    sample_data/sample_student_record.enc --key ../secret.key

# Decrypt it and verify it matches the original
python3 encryption_tool.py decrypt sample_data/sample_student_record.enc \
    sample_data/sample_student_record.dec --key ../secret.key \
    --compare-to sample_data/sample_student_record.txt

# Calculate and save a SHA-256 hash
python3 encryption_tool.py hash sample_data/sample_student_record.txt \
    --save sample_data/sample_student_record.sha256

# Later, verify the file hasn't changed
python3 encryption_tool.py verify sample_data/sample_student_record.txt \
    sample_data/sample_student_record.sha256
```

All commands print `[OK]`, `[FAIL]`, or `[ERROR]` and exit with a non-zero
status code on failure; none of them raise an unhandled exception on a
missing file, empty file, wrong key, or tampered data (see the test
transcript in the report for evidence of each case).

## 3. Firewall rules

Edit the placeholders at the top of `firewall/firewall_rules.sh`
(`GUEST_SUBNET`, `STAFF_SUBNET`, `SERVICE_PORT`, `PROTOCOL`) with the values
given for the authorised laboratory network, then run:

```bash
chmod +x firewall/firewall_rules.sh
./firewall/firewall_rules.sh
sudo ufw status numbered
```

Test evidence and commands are recorded in `firewall/filter_tests.md`.

## 4. Reproducing the tests

1. Run through the "Encryption toolkit usage" commands above in order.
2. Run the firewall script, then execute the three test commands listed in
   `firewall/filter_tests.md` and record the actual output.
3. Compile the report: `cd report && pdflatex report.tex`.

## Security notes

- No real student records, passwords, or encryption keys are committed to
  this repository (`sample_data/` contains dummy data only; `.gitignore`
  excludes `*.key` and any encrypted/decrypted output).
- The Fernet scheme used by `encryption_tool.py` provides both encryption
  and built-in authentication (tamper detection); the separate SHA-256
  hash utility satisfies the integrity-check requirement independently.
