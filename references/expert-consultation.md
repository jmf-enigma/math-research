# Bounded Expert Consultation

Use a stronger or independent model to propose a missing mathematical move, not to certify a proof.

## Admission Gate

Consult only when the proof owner can name the tuple

`(exact claim, assumptions, local subgoal, failed implication, failure witness)`

and at least one of these holds:

- one serious route reaches a nonroutine idea-level kernel that retrieval, CAS, finite search, optimization, or Lean does not directly decide;
- two materially different routes reach the same local obstruction;
- a cold referee attacks one hard local step and the central mechanism otherwise survives.

Do not consult during initial reading, for routine algebra, for a finite leaf with a suitable solver, or to approve a complete proof. Do not send unpublished text, private data, or attachments through a browser bridge without the user's approval.

## Compact Packet

Send only what changes the local decision:

1. Exact claim and domains.
2. Current local subgoal.
3. Assumptions available at that subgoal.
4. Verified prefix or already checked lemmas.
5. Failed route and its exact failure witness.
6. One requested artifact: a new mechanism or construction, a replacement for the failed step, or a decisive refutation.
7. Acceptance test and cheapest falsifier.

Ask for one role only:

- `route`: give one materially new mechanism or construction;
- `surgery`: replace the first failed implication while preserving the route;
- `critic`: refute the proposed kernel or identify its first missing assumption.

Require this response shape:

```text
STATUS: candidate | refutation | no-progress
KERNEL:
DIFFERENCE FROM FAILED ROUTE:
ASSUMPTION MAP:
SHORT DERIVATION:
DECISIVE CHECK OR FALSIFIER:
UNRESOLVED GAP:
```

The consultant must expose the hard step rather than rename the original theorem as a lemma. A useful response has one executable check or a derivation the proof owner can reproduce without trusting the consultant.

## Provider And Budget

If the user explicitly opts in for the current task and an approved Rosetta `consult` MCP tool is available, use its Pro mode with `fresh: true`, no `recall`, and no attachments by default. Rosetta is an optional unofficial browser bridge, not part of this skill and not an official verification channel. Review the provider's current terms before enabling it. If it is unavailable, disclosure is not approved, or the user prefers an official route, use one fresh native subagent or stop with the prepared packet.

Make one call per unchanged proof-state tuple. Permit one follow-up only when the first answer contributes a new checkable kernel and the follow-up asks one precise clarification or falsification question. The hard cap is two calls. A timeout, generic brainstorm, cosmetic rewrite, or answer without a decisive check counts as no progress; retire it rather than retrying. On any rate limit, account restriction, authentication anomaly, or protective challenge, stop immediately and do not retry or work around it.

## Intake Gate

Record the provider, model as reported by the tool, proof-state tuple, response, and disposition when working in durable project mode. Mark the response `proof_effect=none`.

Run the proposed falsifier first. If it survives, independently reconstruct the derivation and check every imported assumption. Promote only the exact portion that is replayed by mathematics, a source, CAS/SMT, Lean, or a cold referee. Never cite the consultation itself as proof authority.
