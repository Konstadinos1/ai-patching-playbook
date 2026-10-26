# AI Patching Playbook

Let an AI agent patch a Linux webserver safely — with a process designed so
the agent **cannot** silently break production.

Three files:

| File | What it is |
|---|---|
| [`HOWTO.md`](HOWTO.md) | The full process, step by step, for humans |
| [`PROMPT.md`](PROMPT.md) | The metaprompt to paste into ChatGPT / Claude Code / any agent |
| [`scripts/audit.sh`](scripts/audit.sh) | Read-only audit script the agent (or you) runs first |

## The 60-second version

1. Run `bash scripts/audit.sh` on the server (read-only, changes nothing).
2. Paste `PROMPT.md` + the audit output into your agent.
3. The agent returns a **plan**. Nothing is executed until you approve it.
4. Approve → agent backs up → patches **one layer at a time** → verifies by
   health checks → reports with evidence.

## The two rules that prevent 90% of disasters

- **Restarts are the dangerous operation**, not the patch. Every restart
  needs: expected downtime, a post-check, and a rollback named in advance.
- **Verify by health, not by silence.** "No errors in the log" is not
  "the service works". Hit the actual endpoint.

## Works in two modes

- **advise** — ChatGPT-style, no server access. Agent reads your pasted
  audit and returns exact commands. You execute.
- **execute** — Claude Code / Codex / Hermes with shell access. Agent runs
  everything but stops at the plan gate for your approval.

## License

MIT — use it, fork it, ship it.
