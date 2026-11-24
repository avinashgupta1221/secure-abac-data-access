# Secure Data Access Layer with Attribute-Based Controls (ABAC)

A runnable, dependency-free Python demonstration of attribute-based access control for a multi-tenant analytics platform.

## Features
- ABAC evaluates **subject**, **resource**, **action**, and **environment** attributes.
- Policy Decision Point (PDP) returns `ALLOW` or `DENY` with policy ID and reason.
- Tenant isolation, active-account checks, MFA/trusted-device checks, classification clearance, region scope, action restrictions, export control, and PII protection.
- Synthetic sample tables are returned only after an `ALLOW` decision.
- SQLite audit log stores timestamp, identity, tenant, resource, action, decision, policy, reason, and attribute context.
- Interactive CLI and command-line mode.
- Unit tests for allow and deny scenarios.

## Requirements
Python 3.10 or newer. No external Python packages are required.

## Run locally
Open a terminal in this folder:

```bash
python app.py
```

Choose a persona, table, and action when prompted. The CLI prints the decision and returns sample rows only if access is allowed. Press `Ctrl+C` to exit.

## Run a single request
```bash
python app.py --user analyst --resource sales_summary --action read
python app.py --user partner --resource customer_profiles --action read
python app.py --user security_admin --resource customer_profiles --action read
python app.py --user analyst --resource sales_summary --action export
python app.py --user analyst --resource sales_summary --action read --no-mfa
```

Available personas: `analyst`, `partner`, `security_admin`, `tenant_b_analyst`.

Available resources: `sales_summary`, `customer_profiles`, `regional_metrics`, `tenant_b_sales`.

## View audit records
```bash
python app.py --audit
```
The default SQLite database is `audit.db`. Use `--audit-db path/to/file.db` to choose another path.

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Policy model
- **Subject attributes:** user ID, tenant ID, account status, clearance, allowed regions, export permission, PII permission.
- **Resource attributes:** resource ID, tenant ID, classification, region, PII marker, allowed actions.
- **Action:** read, query, export.
- **Environment attributes:** trusted-device and MFA verification flags.

## Policy summary
| Policy | Rule | Deny condition |
|---|---|---|
| P-001 | Tenant isolation | Subject and resource tenant differ |
| P-002 | Active identity | Account is not active |
| P-003 | Secure session | Device is untrusted or MFA missing |
| P-004 | Classification | User clearance is below resource classification |
| P-005 | Region scope | Resource region is outside subject scope |
| P-006 | Action | Action is not allowed for the resource |
| P-007 | Export | Subject lacks export permission |
| P-008 | PII | Resource contains PII and subject lacks PII permission |

The PDP uses **default deny**: any condition not explicitly allowed is denied.

## Example scenarios
| Persona | Resource | Expected result | Reason |
|---|---|---|---|
| analyst | sales_summary | ALLOW | Same tenant, internal clearance, west region |
| partner | sales_summary | DENY | Public clearance is insufficient |
| analyst | customer_profiles | DENY | Insufficient clearance / no PII permission |
| security_admin | customer_profiles | ALLOW | Sufficient clearance and PII permission |
| analyst | tenant_b_sales | DENY | Tenant boundary mismatch |
| analyst | sales_summary (export) | DENY | Export permission is false |

## Project structure
```text
secure_abac_data_access/
├── abac/
│   ├── __init__.py
│   ├── audit.py
│   ├── data.py
│   └── policy.py
├── tests/
│   └── test_policy.py
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── README.md
└── PROJECT_REPORT.md
```

## Security and scope notes
This is an educational reference implementation using synthetic in-memory data. It demonstrates authorization logic and auditability; it is not a production identity provider or database security boundary. A production deployment should authenticate users through a trusted identity provider, derive attributes from verified sources, enforce row/column filtering inside the data service, protect audit storage from alteration, use secrets management, and add rate limiting and operational monitoring. Never accept client-supplied attributes as authoritative.
