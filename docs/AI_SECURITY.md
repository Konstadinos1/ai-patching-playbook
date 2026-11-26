# Security architecture for the patching agent

Use this guide when deciding whether an assistant may execute a patch. The service owner owns the workload risk. The operator owns the connection to the target. A model can interpret evidence and propose a change. Giving its runtime credentials also gives model errors and misleading input a path to that workload.

## Decide which authority to delegate

| Operating decision | What the operator needs to establish |
|---|---|
| Allow analysis | Identify which inventory fields may leave the target, the approved recipient or model service, and who can read the retained record. Redact at collection. In advise mode a human checks the proposed action against trusted inputs and uses a separate session to execute it. |
| Allow a bounded change | A trusted executor checks the operator's delegation against the actual target, action, artifact, effects, and window. The agent cannot reach an equivalent write path, change that policy, approve its own request, or alter the approval record. An independent source can verify the outcome. |
| Keep execution with the operator | The available interface grants broader authority than the task requires, the resolved transaction differs from the approved plan, or a prerequisite cannot be established. Keep planning in advise mode while the operator resolves the gap. |
| Hand off to incident response | Evidence suggests the target, artifact source, or execution identity has been compromised. The service owner and incident lead decide how to contain the exposure and preserve evidence before continuing. |

In execute mode, the executor can be an existing deployment service or a restricted operation in a change system. In advise mode, a human applies the checks in a separate session and controls its credentials. This repository supplies the playbook and inventory collector. Each deployment supplies its enforcement mechanisms.

## Follow one patch across its trust boundaries

| Boundary | Security question | Enforcement point and evidence |
|---|---|---|
| Host and scanners → model | Can a service-controlled log line or advisory description change the requested task? Can private package names reach a model, registry, or trace store? | The inventory script prints diagnostics. The operator or a site-managed ingestion service selects approved fields and destinations before sending any output to the model. Keep raw diagnostics in restricted storage. Attach collection time, source and scope to the excerpt. |
| Model → approval system | Can a plausible model summary obscure a different service, artifact, or destination in the underlying request? | The review interface renders the operation and its resolved arguments from the same record the executor will consume. The approver authenticates outside the model session. Store the reviewed revision where the agent cannot replace it. |
| Approval system → executor | Could a stale plan, wrong Docker context, duplicate dispatch, or expired window reach production? | The executor resolves target identity, checks the authorized revision and current deployment state, and correlates each dispatch with a change and step ID. Retain its allow, deny, and completion records outside the target. |
| Executor → host and artifact source | Does the selected operation bring further authority through build scripts, maintainer scripts, mounts, or credentials? | Use a reviewed deployment operation with fixed target selection, controlled arguments and narrowly scoped credentials. Establish which artifact and configuration it activates, which services it can restart, and what network destinations it can reach. Retain the resolved transaction or deployment receipt. |
| Target → closure decision | Could a successful exit or model-generated summary hide an old active process, a different artifact, or failed user requests? | Compare the execution receipt and active identity with the independent workload observer and applicable advisory evidence. A conflicting reading leaves the corresponding claim open. |

For example, removing a deploy tool provides little isolation if the same assistant retains write access to a manifest that automatically deploys, a general shell with deployment credentials, or the Docker daemon. Trace authority through each reachable interface, including build and delivery systems. Read access also deserves a destination check when a scanner can transmit a dependency inventory.

If the assistant uses persistent memory or retrieves earlier change records, scope that store to the workload and its readers. An old incident note may accurately describe a restart that was approved last month. Treat the note as historical evidence. Only the current approval record can delegate today's restart. Record which source revision entered the session so an owner can quarantine or correct stale material.

### Decide what the assistant may see

For an npm finding, the model may need the affected package, installed and fixed revisions, advisory reference, and deployment scope. The configured registry may receive dependency metadata during the scan. The model provider and trace store receive whatever the application forwards to each. Authorize these transfers separately. A registry approved for private dependencies does not confer permission to send the same inventory to a hosted model.

Filter fields before sending the request, including tool arguments, results and error paths. Apply workload and reader access checks before retrieving prior records. If a document's access changes, invalidate affected retrieval and response caches. Record the provider's applicable retention and training-use settings separately from your own transcript, debug-log and backup retention. A provider can retain a request for a period even where training use is disabled.

## Bind approval to the effective operation

Use the [change plan](../templates/CHANGE_PLAN.md) to capture the decision. In a tool-backed deployment, the execution service can keep the following details in its own authenticated change record.

| Record | Values to bind |
|---|---|
| Who and when | Approver, delegated executor identity, change and revision, validity window, and revocation status |
| What and where | Stable environment and target IDs, layer and service, current and proposed artifact identities, configuration or deployment procedure revision, and any approved endpoints |
| How far | Allowed steps and effects, maximum workload scope and interruption, canary and observation gates, and separately authorized recovery actions |

**Before dispatch**, read the reviewed record from the change system. Resolve host and service through a trusted inventory. Compare the observed current artifact, procedure and candidate with the approved values. For a distro package, compare the full resolved package set and revisions. For Compose, check the project, daemon endpoint, effective manifest revision and platform-specific image identity. A digest binds bytes. Publisher identity and permitted release origin require separate provenance evidence.

**When state can change concurrently**, use a deployment lock or a conditional update against the expected release revision where available. Re-read the preconditions at the point of dispatch. If the platform leaves a race between check and use, record who controls concurrent changes and whether the remaining risk permits execution. A new revision or expanded effect goes back to the approver. A still-valid approval covers the steps already inside its scope.

**When a reply is lost**, preserve the change ID and step ID. Check the executor's operation history and the observed workload before retrying. The executor should recognize duplicate submissions where supported. An ambiguous result such as an accepted deployment followed by a client timeout stays unknown until reconciled. Hold the next wave during reconciliation. Window expiry or revocation blocks new actions. An accepted operation may still be running and needs its own containment or recovery decision.

## A decision at the console

Suppose an operator approves moving a fictional staging API from release A to B on one Compose host. The deployment record identifies the host, API service, matching manifest revision, and an allowed API restart. An audit excerpt claims the database must also be restarted and describes a broader operation as already approved. The planner can record that claim and seek corroborating evidence. The executor derives authority from the recorded operation and rejects a database restart. An operator following an advise-mode plan makes the same comparison before acting.

Just before dispatch, the executor finds release C already running on the approved host. Even though B is still an approved candidate, the A-to-B transition no longer describes this change. Deploying B could undo a newer fix, and the planned rollback to A now restores the wrong baseline. Hold the request, identify the intervening deployment and ask the owner to reassess the finding and recovery target. Record the denied transition and the observed C identity in the change report.

OWASP's guidance on excessive agency and indirect prompt injection covers the underlying risks of delegating tool access to a language model. [Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) · [LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
