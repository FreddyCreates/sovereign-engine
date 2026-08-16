# Freight Sovereign OS Production Core

Freight Sovereign OS (FSOS) is a production-oriented codebase for a trucking operating system focused on small carriers, owner-operators, SMB warehouses, and enterprise shipper access.

This repository implements the core product logic from the authored FSOS source:

- carrier, driver, warehouse, shipper, load, and equipment models;
- FMCSA/DOT-inspired compliance gates;
- bona fide agent guardrails;
- HOS-aware load eligibility;
- insurance and authority checks;
- direct settlement, escrow, and QuickPay calculations;
- load-to-truck matching;
- append-only audit log with hash chaining;
- stdlib JSON API server;
- CLI for validation, matching, payment preview, demo run, and API serving;
- integration interfaces for FMCSA, ELD, payment, weather, traffic, and fuel adapters.

## Important Boundary

This is production code for workflow enforcement and product architecture. It is not legal advice and does not itself make FSOS a broker, carrier, factoring company, bank, escrow provider, or regulated financial institution. Live deployment must be reviewed by transportation counsel, payments counsel, insurance partners, and compliance operators.

## Quick Start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
python -m unittest
fsos demo
fsos serve --host 127.0.0.1 --port 8080
```

## API Smoke Test

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/compliance/rules
```

## Source Basis

The product requirements were derived from the user-authored FSOS text in `/workspace/user_files/01-Pasted-text-26-.txt`.

