# Review the action record

Classify five fictional patching actions using the approved change, the agent's account and independent observations. For each case, name the record that supports your decision and the next action the operator should take. This tabletop measures a reviewer's interpretation of supplied evidence. Deployment assurance requires observations from the actual tool and backend.

From the repository root, display the cases with Python 3.9 or later. The reader runs offline, prints to the terminal and exits.

```sh
python3 exercises/review.py
```

| Answer | What the records establish for the named action |
|---|---|
| `denied` | The action was blocked before it could take effect, with coverage of the relevant paths. |
| `violation` | An observed effect exceeded the approved scope. |
| `unknown` | The available records leave the effect unresolved. |
| `completed` | The approved action took effect on its intended target. Assess workload health and the next wave separately. |

Use `python3 exercises/review.py CASE --answer VERDICT` to check a single answer. Replace `CASE` with the case letter and `VERDICT` with your judgment from the table. Use `python3 exercises/review.py --key` for the full answer key and operator decisions. A correct answer returns exit code 0, a wrong answer returns 1, and invalid command arguments return 2.

The fixtures use short artifact labels such as R4 for readability. Each label represents a single verified immutable artifact identity within that case. The approval, controller, target, observer and proxy records are stipulated facts for the exercise. In an actual incident, verify the origin, integrity, timestamps and coverage of each record.
