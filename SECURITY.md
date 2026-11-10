# Security policy

This project provides operational guidance and an inventory script. A defect in parsing, command construction, secret handling, or patching advice can affect users who apply it. A passing test suite does not establish production safety; see [support and validation boundaries](docs/SUPPORT.md).

## Report a sensitive issue

Use the repository's **Security → Advisories → Report a vulnerability** option if GitHub private vulnerability reporting is available. Availability depends on repository settings; this document does not claim it is enabled.

If private reporting is unavailable, open a minimal, redacted issue asking the maintainer to establish a private reporting channel. Do not include exploit details, credentials, host identities, private audit output, or an affected customer's data in that public issue. Wait for a private channel before sharing sensitive details.

For a private report, include the affected repository revision, relevant platform/tool versions, expected and actual behavior, a minimal synthetic reproduction, impact, and possible mitigation if known. Keep full production evidence in your own access-controlled storage.

Ordinary documentation questions and non-sensitive bugs can use public issues. Do not test an exploit against systems you are not authorized to assess. Suspected compromise of a live host belongs with that host's incident-response owner; patching this repository does not investigate or remove compromise.

## Handling and scope

Maintainers can triage reports, reproduce them in isolation, coordinate a correction, and publish an advisory or release note when appropriate. This project makes no guaranteed response-time or remediation-time commitment. Avoid public disclosure of sensitive details while a private report is being assessed.

Report defects in this repository here. For a vulnerability in an upstream package, registry, operating system, or container image, use that vendor's security process; do not assume this repository maintains the affected component.

The default branch is the current maintenance target. Earlier revisions require case-by-case review; there is no promised backport or long-term-support schedule. The [support policy](docs/SUPPORT.md) separates intended platforms from demonstrated validation.
