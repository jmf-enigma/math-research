#!/usr/bin/env python3
"""Print a compact proof-idea map with optional discovery or control detail."""

from __future__ import annotations

import argparse
import textwrap

from start_proof import central_lemma_suggestions, idea_rows, select_playbooks


def wrap(text: str) -> str:
    return textwrap.fill(text, width=88, subsequent_indent="  ")


def focused_playbooks(selected: list[tuple[str, int]]) -> list[tuple[str, int]]:
    if not selected:
        return selected
    if selected[0][1] >= 2 and (
        len(selected) == 1 or selected[0][1] - selected[1][1] >= 2
    ):
        return selected[:1]
    return selected[:2]


def print_compact(claim: str, selected: list[tuple[str, int]]) -> None:
    print("Mode")
    print("- Try direct proof first; use this map only if no named theorem, certificate, contradiction, or known decomposition closes the claim.")

    print("\nSelected playbooks")
    for name, value in selected:
        print(f"- {name} (score {value})")

    print("\nStatement and failure world")
    print(f"- claim: {claim}")
    print("- statement fence: exact variables, domains, assumptions, quantifiers, and conclusion")
    print("- negation: write the smallest object that would falsify the claim")
    print("- first stress test: smallest finite/scalar/boundary/relaxed-assumption case")

    print("\nCentral-object candidates")
    for obj, failure, assumptions, hook in idea_rows(selected)[:6]:
        print(f"- {obj}: controls {wrap(failure)}")
        print(f"  assumptions: {wrap(assumptions)}")
        print(f"  verification: {wrap(hook)}")

    print("\nKernel candidates")
    for line in central_lemma_suggestions(selected).splitlines():
        print(line)

    print("\nChoose one next artifact")
    print("- State one kernel: local claim, implication for the theorem, evidence type, and failure shape.")
    print("- Make one falsifiable local prediction and name the cheapest observation that would keep or retire the idea.")
    print("- Choose one proof route. Attach one falsifier and, only if needed, one orthogonal check; they test the route rather than form parallel proof portfolios.")
    print("- Continue only with a route that controls the failure world and has a verification hook.")
    print("- If no kernel appears, retrieve one close theorem pattern or repair the statement; do not draft a long proof.")


def print_discovery() -> None:
    print("\nExtended search")
    print("- Select exactly one move below that matches the named obstruction; do not execute the list as a workflow.")
    print("- Discovery: if a threshold, potential, policy, hard instance, active set, coefficient, or exact answer is unknown, infer it from tiny/tight cases and reserve a holdout check.")
    print("- Unknown answer or object: freeze its admissible type, exact validity check, and one holdout before search; forbid target-restating answers.")
    print("- Bottleneck surgery: shrink and negate the missing lemma, then move one rung on the representation ladder before proving, falsifying, retrieving, certifying, or repairing it.")
    print("- A failed bounded witness search may suggest a rigidity or invariant conjecture; it creates a new proof obligation and never proves the target.")
    print("- Construction seeds: dual/slack, Bellman gap, envelope term, deviation graph, coupling, KL bridge, potential, benchmark, or hard instance.")
    print("- Algebra forms: add-subtract benchmark, gap/telescope, completing square, conjugate/dual, log/KL/determinant, symmetrization, or conditioning on a good event.")
    print("- Certificate-first: write the checkable certificate conditions, then solve backward from the conclusion and tight case for the simplest object that satisfies them.")
    print("- Local-to-global: pair one local exchange, derivative, deviation, or drift fact with the exact convexity, lattice, envelope, Bellman, or induction principle that globalizes it.")
    print("- Abstraction-refinement: start from the smallest faithful model, refine only the feature responsible for failure, and keep the surviving invariant as a new lemma target.")
    print("- Bottom-up synthesis: prove or refute at most two special cases or auxiliary facts, then infer the shared invariant or strengthening instead of accumulating side lemmas.")
    print("- Equality-driven algebra: impose boundary and zero-slack conditions, fit the smallest ansatz, reserve a holdout, and factor the exact residual to expose the real lemma.")
    print("- Trick replay: migrate a paper move only through its assumptions, transformation, output artifact, verifier, and failure mode.")
    print("- Representation witness: give the concrete map, admissible image, and implication back; require only the directions the target needs, not an unnecessary bijection.")
    print("- Failed closure: derive the residual or operation that breaks the construction, then try one additional invariant or coordinate and prove its preservation.")
    print("- Refutation scope: distinguish a witness against the original theorem, a child lemma, and a faulty encoding before repairing the statement.")
    print("- Good-gap test: require the kernel to be smaller, non-circular, assumption-explicit, and locally checkable.")


def print_controls() -> None:
    print("\nFrontier and answer controls")
    print("- Novel problem: treat memory as unverified; first scan Scholar/recent public work and verify the closest result and frontier gap, then define the candidate representation, exact evaluator, simplification ladder, promotion rule, and budget. For construct or find-all tasks, freeze the answer type, forbid target-restating answers, and separate witness soundness from completeness.")

    print("\nOne-move control")
    print("- Record current subgoal, proposed move, expected artifact, check, and proof-state delta.")
    print("- Quotient exact theorem-preserving symmetries before counting routes; replay transported artifacts on the original statement.")
    print("- Reserve a verification-and-assembly tail budget; renew an expensive route only after a checked proof-state delta.")
    print("- After two unchanged moves, choose repair, re-decompose, retrieve, tool-falsify, theorem repair, or stop-report.")
    print("- Do not count a new prompt, agent, temperature, or larger sample as a new route unless it strengthens the evaluator or changes the artifact type.")
    print("- Use a prover-verifier contract only for challenged, repeated, or hard-to-check moves.")
    print("- Merge attempts with the same goal, assumptions, central object, and failure witness.")
    print("- Build retries from a solver-owned digest of exact checker output; reuse prior wins only as precondition-matched templates with exact replay.")

    print("\nOptional matched strategy trial")
    print("- Activate only when repeated project cycles make route control itself the bottleneck.")
    print("- Compare at most two stage-appropriate policies on the same proof-state baseline, references, tools, and budget.")
    print("- Record one artifact, first failure, and proof-state delta per policy; relative ratings have proof_effect=none.")
    print("- Promote guidance only after a second-state or held-out gain, and retire it when the stage or failure fingerprint changes.")

    print("\nEvidence-layered search packet")
    print("- Activate only after direct solve fails and candidate rules become noisy or repetitive; keep it to one screen.")
    print("- Sound shortcuts: record preconditions, resulting obligation, checker, and exact proof effect.")
    print("- Executable falsifiers: verify every premise over every required assignment, exhibit target failure, and label exhaustive versus sampled scope.")
    print("- Scheduler priors: similarity, size, source hits, scores, and failure history always have proof_effect=none.")
    print("- Near-miss frontier: keep 2-4 checked or rejected states with verified prefix, exact gap, and candidate bridge.")
    print("- Promote only a replayable derivation, counterexample/certificate, source-checked theorem use, or formal check.")
    print("- Seed reusable trick memory only after exact replay plus an independent route or held-out check.")
    print("- Audit term ranges before arbitrary substitution: prove surjectivity, and keep diagonal laws distinct from global laws.")

    print("\nOutside patterns and tools")
    print("- Scan one to three close sources only when the theorem family, central object, or standard lemma is missing.")
    print("- Extract assumptions, proof decomposition, local trick, verification hook, and mismatch; do not import prose as proof.")
    print("- Before a tool call, name the local claim, domain, negation, expected artifact, and translation back into proof.")
    print("- Audit Lean/API artifacts for `sorry`, admitted axioms, unresolved obligations, and missing assembly.")


def print_full() -> None:
    print_discovery()
    print_controls()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("claim", help="The theorem, lemma, or proof goal")
    detail = parser.add_mutually_exclusive_group()
    detail.add_argument(
        "--discovery",
        action="store_true",
        help="Add only high-leverage construction and idea-discovery moves",
    )
    detail.add_argument(
        "--full",
        action="store_true",
        help="Add discovery, repair, retrieval, evidence, and tool-control details",
    )
    parser.add_argument("--include-paper-queries", action="store_true", help="Print claim-specific literature search prompts")
    args = parser.parse_args()

    selected = focused_playbooks(select_playbooks(args.claim))
    print_compact(args.claim, selected)
    if args.full:
        print_full()
    elif args.discovery:
        print_discovery()
    if args.include_paper_queries:
        from proof_doctor import external_pattern_queries

        print("\nSearch prompts")
        for query in external_pattern_queries(args.claim, selected):
            print(f"- {query}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
