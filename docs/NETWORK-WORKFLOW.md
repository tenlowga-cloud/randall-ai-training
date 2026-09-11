# Randall's first useful network workflow

Begin with a synthetic or approved lab change, not production access. Ask which vendor, software version, source of truth and existing automation framework apply. Read the current approved configuration and the desired outcome; distinguish observed state from intended state.

1. Identify the affected topology, dependencies, traffic flow, management access and failure domain. Keep unknowns visible.
2. Produce a minimal candidate diff with vendor/version-specific official documentation. Never guess interface names, credentials, routing policy or live addresses.
3. Have a Sol worker validate syntax and invariants using available offline parsers or a lab. Give Claude the approved candidate for a bounded review of assumptions and missing tests when useful.
4. Write prechecks, expected observations, change order, abort conditions, validation and rollback. Include how management access is retained. A generated configuration is a proposal until tested.
5. Randall decides whether and when a production change is authorized. The starter bridge cannot apply device configurations.
6. Save the candidate in its code/config owner. Link its revision, test evidence, decision and reusable correction from the Obsidian project. Begin the next session by retrieving that correction.

Example exercise: VLAN 20 uses documentation subnet 192.0.2.0/24. Draft a change plan with explicit missing inputs; do not invent a gateway or switch platform. Acceptance: the plan asks for required facts, includes validation and rollback, and makes no device connection.
