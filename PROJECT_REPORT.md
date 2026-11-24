# Project Report: Secure Data Access Layer with Attribute-Based Controls

## 1. Introduction
Analytics platforms often serve multiple organizations, teams, and external partners. A user who can access one tenant's data must not automatically gain access to another tenant's data. Traditional role-only checks can be too broad for these situations. Attribute-Based Access Control (ABAC) makes decisions using attributes of the subject, resource, requested action, and environment.

## 2. Objective
The objective is to design and implement a secure data access layer that evaluates ABAC policies, returns allow/deny decisions, records each decision for audit, and demonstrates the result through a command-line interface.

## 3. ABAC Model
The implementation evaluates four dimensions:
- **Subject:** user ID, tenant, account status, clearance, allowed regions, export permission, and PII permission.
- **Resource:** table ID, tenant, classification, region, PII marker, and allowed actions.
- **Action:** read, query, or export.
- **Environment:** trusted-device and multi-factor-authentication status.

## 4. Architecture
1. The CLI receives a selected persona, resource, and action.
2. It constructs an access request containing subject, resource, action, and environment attributes.
3. The Policy Decision Point evaluates the request against ordered policies.
4. The PDP returns an explicit ALLOW or DENY decision with a policy identifier and reason.
5. The audit logger persists the decision and relevant context in SQLite.
6. The sample data layer returns records only when the decision is ALLOW.

## 5. Policy Enforcement
The policy set checks tenant isolation, active account status, secure session requirements, classification clearance, region scope, permitted action, export permission, and PII permission. Unknown or insufficient attributes fail closed. This reduces the chance that missing information accidentally grants access.

## 6. User Personas and Scenarios
- **Analyst:** active Tenant A user with internal clearance, west/north region access, and no export or PII permission.
- **Partner:** active Tenant A user with public clearance and west-only scope.
- **Security administrator:** active Tenant A user with restricted clearance, broad region scope, export permission, and PII permission.
- **Tenant B analyst:** active Tenant B user, used to demonstrate tenant isolation.

The test suite verifies successful access to permitted sales summaries and denial of insufficient clearance, out-of-scope region, cross-tenant access, missing MFA, and unauthorized export.

## 7. Audit Logging
Every evaluated request is written to SQLite with a UTC timestamp, subject ID, tenant ID, resource ID, action, effect, policy ID, reason, and JSON context containing subject, resource, and environment attributes. The CLI provides an audit-view command.

## 8. Testing
Automated unit tests cover the main allow and deny conditions and verify that an audit event is persisted. Run them using:

```bash
python -m unittest discover -s tests -v
```

## 9. Conclusion
The project demonstrates how ABAC supports fine-grained access decisions in a multi-tenant analytics setting. Combining tenant boundaries, clearance, region, action, environment, and data-sensitivity attributes provides more precise control than a single role check. Default-deny behavior and audit logging make decisions easier to review and troubleshoot.

## 10. Future Enhancements
A production-ready version could integrate an identity provider, external policy administration, signed policy bundles, row-level SQL filtering, encrypted audit storage, dashboards, and centralized monitoring.
