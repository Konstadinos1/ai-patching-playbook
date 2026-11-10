# Threat model for AI-assisted patching

Scope: the operator, agent, repository instructions, inventory/scanner inputs, execution account, artifact supply chain, recovery material, and change evidence. This is a design review aid, not a penetration test or a claim that every listed control is implemented by the repository.

## Assets and assumptions

Protect service availability, state integrity, credentials, deployable artifacts, and the accuracy of approval/evidence records. Assume the target may contain attacker-controlled filenames, logs, application data, and package text. External advisories/scanners can fail or be stale. The agent may misunderstand instructions or lose its session. A fully compromised execution host can tamper with local evidence; corroborate with independently trusted sources and follow incident response when compromise is suspected.

## Failure and abuse cases

| Threat or failure | Concrete path | Control and verification | Remaining limit |
|---|---|---|---|
| Prompt injection | A log or scanner description tells the agent to upload credentials or skip approval | Treat inputs as data; keep approvals in a separate human-owned record; restrict tools/egress; test the agent with an inert malicious-text fixture in a lab | Prompt rules alone cannot contain a privileged agent |
| Wrong host or Docker context | Commands affect a different account, cluster, or remote daemon | Record resource IDs, environment, execution identity, Docker context/endpoint, and target confirmation before mutation | Hostname alone can be ambiguous or spoofed |
| Dependency metadata disclosure | Network scan sends private package names to a registry | Approve destination/scope, inspect configured registry, limit output, use protected evidence storage | Default local inspection still depends on configured clients/contexts |
| Artifact substitution or tag drift | Mutable tag changes between approval and deploy | Resolve trusted artifact to immutable identity; validate provenance per policy; compare approved, scanned, and active digests | A digest fixes identity, not publisher trust or safety |
| Privilege escalation through tooling | Docker socket or broad sudo gives the agent host control | Use a restricted account and reviewed command/tool authorization; independently audit actual permissions | Docker group membership is highly privileged |
| Shell/path injection | Untrusted path or package text is concatenated into commands | Use structured arguments and quoted paths; review exact commands; do not use `eval` on evidence | An agent's generated command still needs review |
| False clean result | Registry failure, stale indexes, or malformed JSON becomes zero findings | Preserve exit status, validate result shape, label missing coverage UNKNOWN, test error paths | Valid scanner output can still have incomplete coverage |
| Hidden restart or session loss | Maintainer script restarts SSH, supervisor, or the agent host | Include automatic restart effects in approval; independent console, observer, and durable recovery packet | A prompt cannot override package-manager behavior |
| Unsafe rollback | Old application starts against migrated state, or volume backup is missing | Verify state compatibility and backup scope/restore rehearsal before patching | Artifact retention alone does not recover data |
| Evidence manipulation or leakage | Logs are overwritten or public reports contain credentials | Keep timestamped, access-controlled evidence outside the target; redact public records; corroborate with external monitoring | Checksums detect changed bytes only if the recorded checksum is trustworthy |
| CI supply-chain exposure | Untrusted PR code executes in a workflow with secrets/write token | Run repository checks with read-only permissions, no production credentials, pinned Actions, and reviewed dependency updates | Passing CI is not a security review or production recovery test |

## Review triggers and lab exercises

Revisit this model when adding a scanner, permission, remote target, agent runtime, backup provider, or deployment layer. For each new integration record what it can read, mutate, transmit, restart, and authorize.

Use an isolated disposable environment for exercises: confirm a failed scanner stays unknown; confirm wrong-target detection aborts; simulate losing the agent during a restart; restore a prior artifact with representative state; and verify an inert prompt-injection instruction in a log is ignored. Record tool/agent versions, expected behavior, actual result, evidence, and remaining gaps. Do not claim these exercises have run until their results are available.
