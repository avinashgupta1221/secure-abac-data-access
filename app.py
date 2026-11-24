"""Interactive CLI demonstration of a multi-tenant ABAC data access layer."""
import argparse
import json
from abac.data import USERS, RESOURCES, TABLE_DATA
from abac.policy import AccessRequest, PolicyDecisionPoint
from abac.audit import AuditLogger

def print_result(user_key, resource_key, action, request, decision, rows):
    print("\n" + "=" * 68)
    print(f"SUBJECT: {user_key} ({request.subject['user_id']})")
    print(f"RESOURCE: {resource_key} | ACTION: {action}")
    print(f"DECISION: {decision.effect} | POLICY: {decision.policy_id}")
    print(f"REASON: {decision.reason}")
    if decision.effect == "ALLOW":
        print("DATA:")
        print(json.dumps(rows, indent=2))
    else:
        print("DATA: <not returned>")
    print("=" * 68)

def run_demo(user_key, resource_key, action, trusted, mfa, pdp, audit):
    if user_key not in USERS:
        raise ValueError(f"Unknown user '{user_key}'. Choose from: {', '.join(USERS)}")
    if resource_key not in RESOURCES:
        raise ValueError(f"Unknown resource '{resource_key}'. Choose from: {', '.join(RESOURCES)}")
    # Do not expose the display-only summary as a policy attribute.
    subject = {k: v for k, v in USERS[user_key].items() if k != "attributes_summary"}
    request = AccessRequest(
        subject=subject,
        resource=RESOURCES[resource_key],
        action=action,
        environment={"trusted_device": trusted, "mfa_verified": mfa}
    )
    decision = pdp.evaluate(request)
    audit.log(request, decision)
    rows = TABLE_DATA[resource_key] if decision.effect == "ALLOW" else None
    print_result(user_key, resource_key, action, request, decision, rows)
    return decision

def main():
    parser = argparse.ArgumentParser(description="Secure ABAC Data Access Layer demo")
    parser.add_argument("--user", choices=USERS, help="Persona key")
    parser.add_argument("--resource", choices=RESOURCES, help="Sample table")
    parser.add_argument("--action", choices=["read", "query", "export"], default="read")
    parser.add_argument("--untrusted-device", action="store_true", help="Simulate untrusted device")
    parser.add_argument("--no-mfa", action="store_true", help="Simulate missing MFA")
    parser.add_argument("--audit", action="store_true", help="Show recent audit entries")
    parser.add_argument("--audit-db", default="audit.db")
    args = parser.parse_args()

    pdp, audit = PolicyDecisionPoint(), AuditLogger(args.audit_db)
    if args.audit:
        for entry in audit.recent():
            print(json.dumps(entry, indent=2))
        return
    if args.user and args.resource:
        run_demo(args.user, args.resource, args.action, not args.untrusted_device,
                 not args.no_mfa, pdp, audit)
        return
    if args.user or args.resource:
        parser.error("--user and --resource must be supplied together")

    print("\nSECURE DATA ACCESS LAYER — ABAC DEMO")
    print("Personas:")
    for key, user in USERS.items():
        print(f"  {key:18} {user['attributes_summary']}")
    print("\nResources:")
    for key, resource in RESOURCES.items():
        print(f"  {key:20} {resource['classification']} | {resource['region']} | tenant={resource['tenant_id']}")
    print("\nEnter a demo request (Ctrl+C to exit).")
    while True:
        try:
            user_key = input("\nPersona: ").strip()
            resource_key = input("Resource/table: ").strip()
            action = input("Action [read/query/export]: ").strip().lower() or "read"
            trusted = input("Trusted device? [Y/n]: ").strip().lower() not in ("n", "no")
            mfa = input("MFA verified? [Y/n]: ").strip().lower() not in ("n", "no")
            run_demo(user_key, resource_key, action, trusted, mfa, pdp, audit)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Audit log saved.")
            break
        except ValueError as exc:
            print(f"Input error: {exc}")

if __name__ == "__main__":
    main()
