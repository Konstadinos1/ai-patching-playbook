# Prioritization and time-limited risk acceptance

Use this decision record with the [change plan](../templates/CHANGE_PLAN.md). It supports judgment; it is not a CVSS replacement, compliance attestation, or universal remediation SLA.

## Triage a finding

1. **Confirm identity and applicability.** Identify the deployed artifact and affected distribution/package revision or dependency path. Capture the advisory, fixed version, scan time, and database freshness. Mark missing evidence unknown rather than not affected.
2. **Assess exploitation and access.** Is exploitation known, including verified KEV membership? Is the vulnerable path reachable from the internet, a tenant, or an internal user? Are exploit prerequisites actually met? Internet exposure is not required for high impact.
3. **Assess consequences.** Consider privileges, sensitive data, lateral movement, integrity, service criticality, and blast radius. Separate compromise evidence from patch urgency; suspected compromise needs incident response.
4. **Assess change and recovery risk.** Evaluate compatibility, automatic restarts, redundancy, state migrations, recovery confidence, RPO/RTO, and available mitigations. A dangerous patch can require staged testing without making the underlying vulnerability less severe.
5. **Select a response and deadline.** Record the accountable owner, decision time, target action/deadline with timezone, and why the urgency fits this service. Follow organizational obligations where applicable; do not invent them from this guide.

| Decision band | Typical trigger | Expected handling |
|---|---|---|
| Incident / emergency | Suspected compromise, or applicable active exploitation with material exposure | Engage incident/change owner immediately; choose emergency fix or authorized containment and record recovery limits |
| Expedited change | Reachable high-impact flaw, important control failure, or urgent vendor direction | Assign a near-term deadline based on exposure, validate a bounded fix, monitor until closed |
| Planned change | Applicable flaw with constrained exposure and no urgent exploitation evidence | Assign a scheduled window and owner; validate assumptions before the window |
| Investigate / incomplete | Unknown deployed version, failed scan, unclear applicability | Assign an evidence-gathering deadline; do not label clean or silently defer |
| Not affected | Evidence proves the deployed artifact or use does not meet the advisory's affected conditions | Preserve rationale and source; re-evaluate on deployment or advisory changes |

Severity scores are inputs, not a queue sorter. A low-scoring prerequisite flaw can matter in an exploit chain; a high score alone does not establish this deployment is affected. Image age and total finding counts do not establish either condition.

## When a fix cannot proceed

Use [the risk exception template](../templates/RISK_EXCEPTION.md). The service/risk owner may accept the specific residual exposure for a limited period. The agent cannot accept risk on the owner's behalf. A change approver authorizing a patch is not automatically accepting indefinite exposure from a deferred fix.

An exception needs a verified finding, reason for deferral, evaluated alternatives, measurable compensating controls, named owner, explicit expiry, remediation plan, and review triggers. Where evidence is incomplete, accept the uncertainty explicitly and assign an investigation deadline instead of claiming the risk is known.

Compensating controls must be tested: “behind a firewall” is insufficient without verified path restrictions. Record who checked the control, when, and what traffic or access it actually blocks. Do not paste sensitive network topology or credentials into a public issue.

## Reassessment and closure

Reassess when exploitation/KEV status changes, exposure changes, a control fails, the fixed release becomes available, the workload changes, or the exception expires. Expiry means review/escalation; it does not authorize an unplanned production mutation. No silent renewal: record a new owner decision and expiry.

Close a finding with the approved artifact identity, activation evidence, targeted scan/advisory disposition, and workload verification. Close an exception when remediation is verified or applicability is disproved with evidence. A successful deploy, reboot, or lower aggregate count alone is insufficient.
