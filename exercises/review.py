"""Offline tabletop for reviewing fictional patching-agent action records."""

import argparse
from dataclasses import dataclass
from textwrap import fill


@dataclass(frozen=True)
class Case:
    action: str
    approval: str
    claim: str
    records: tuple[str, ...]
    outcome: str
    reasoning: str


OUTCOMES = ("denied", "violation", "unknown", "completed")
CASES = {
    "A": Case(
        action="Send the dependency inventory to a registry.",
        approval="CH-11 r1 permits a local lockfile read for the staging API.",
        claim="The assistant reports that the registry lookup was blocked.",
        records=(
            "An advisory attachment describes external scanning as pre-approved.",
            "The gateway records a denial for request A-1 before dispatch. "
            "All outbound paths for this session pass through one egress proxy. "
            "Its complete session record shows zero outbound requests.",
        ),
        outcome="denied",
        reasoning="The approval covers local inspection. The gateway decision and "
        "independent egress record support a block for this transfer. Record the "
        "attempt and its source. The local read can still proceed.",
    ),
    "B": Case(
        action="Recreate the staging API canary using artifact R2.",
        approval="CH-12 r2 covers a single recreate on canary-1 during this window.",
        claim="The assistant reports that the operation timed out and can be retried.",
        records=(
            "The dispatcher acknowledges handing B-1 to the controller. The client "
            "times out before receiving a result. Controller history is unavailable.",
            "The last identity sample on canary-1 predates dispatch. A public "
            "health request succeeds on a different replica.",
        ),
        outcome="unknown",
        reasoning="Delivery is confirmed and completion is unresolved. Pause retries. "
        "Reconcile B-1 with controller history and the identity on canary-1 before "
        "deciding whether another operation is needed.",
    ),
    "C": Case(
        action="Send the staging API's package inventory to registry.example.",
        approval="CH-13 r1 authorizes local inventory only. The package inventory "
        "is classified as internal to the exercise tenant.",
        claim="The assistant reports that it refused the external lookup.",
        records=(
            "The scan tool records a denial for C-1. A separate helper used by "
            "the same session generated request C-2.",
            "The egress proxy records delivery of C-2 to registry.example. The "
            "mock receiver's receipt for C-2 identifies the internal fixture "
            "inventory by its matching content digest.",
        ),
        outcome="violation",
        reasoning="The receiver and egress records establish an unauthorized transfer "
        "through the helper. Preserve both request IDs, suspend that session's "
        "egress and scope the disclosure with the data owner.",
    ),
    "D": Case(
        action="Activate the reviewed API artifact R4 on canary-1.",
        approval="CH-14 r3 permits one deployment of R4 to canary-1. The gate "
        "requires a functional request and ten minutes of observations before expansion.",
        claim="The assistant requests a rollout decision.",
        records=(
            "The controller's terminal receipt D-1 matches the approved target, "
            "artifact, plan revision and window. The target inventory ties the "
            "running process on canary-1 to R4.",
            "The independent observer records a passing functional request and "
            "error and latency values within approved limits for ten minutes.",
        ),
        outcome="completed",
        reasoning="D-1 and the target readback confirm the approved activation. "
        "The canary gate passed. This approval covers one deployment. A further "
        "wave needs its own scope in the change record.",
    ),
    "E": Case(
        action="Activate the reviewed API artifact R5 on canary-2.",
        approval="CH-15 r4 covers one activation of R5 on canary-2 in this window. "
        "A worker transaction is required before the rollout can continue.",
        claim="The assistant reports that its client connection dropped.",
        records=(
            "After reconnection, controller history shows a terminal success for "
            "E-1 under CH-15 r4 in the window. An independent target readback ties "
            "the new running process on canary-2 to R5.",
            "The observer has no worker transaction result for this deployment.",
        ),
        outcome="completed",
        reasoning="The controller receipt and target readback resolve the timeout. "
        "Record activation as complete and the worker check as unverified. Hold "
        "the rollout and run the approved check without repeating activation.",
    ),
}


def show_case(case_id: str, case: Case) -> None:
    print(f"\n{case_id}. {case.action}")
    for label, detail in (("Approval", case.approval), ("Agent claim", case.claim)):
        print(fill(f"{label}: {detail}", subsequent_indent="  "))
    for record in case.records:
        print(fill(f"Record: {record}", subsequent_indent="  "))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", nargs="?", choices=CASES, help="show one case")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--answer", choices=OUTCOMES, help="score one case")
    mode.add_argument("--key", action="store_true", help="show the answer and reasoning")
    args = parser.parse_args()
    if args.answer and args.case is None:
        parser.error("--answer requires a case ID")

    print("Classify the named action as denied, violation, unknown, or completed.")
    for case_id in ([args.case] if args.case else CASES):
        case = CASES[case_id]
        show_case(case_id, case)
        if args.key or args.answer:
            print(fill(f"Answer: {case.outcome}. {case.reasoning}", subsequent_indent="  "))
        if args.answer:
            correct = args.answer == case.outcome
            print("Correct." if correct else "Review the action records and try again.")
            return 0 if correct else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
