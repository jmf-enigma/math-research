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
    print("Claim")
    print(f"- {claim}")
    print("- Preserve domains, assumptions, quantifiers, and conclusion. These hints have proof_effect=none.")
    print("\nSelected playbooks")
    for name, value in selected:
        print(f"- {name} (score {value})")
    print("\nCandidate objects")
    for obj, failure, assumptions, hook in idea_rows(selected)[:6]:
        print(f"- {obj}: controls {wrap(failure)}")
        print(f"  assumptions: {wrap(assumptions)}")
        print(f"  check: {wrap(hook)}")
    print("\nCandidate kernels")
    print(central_lemma_suggestions(selected))
    print("\nNext decision")
    print("- Select one exact implication, show how it closes the target, and name a decisive falsifier.")
    print("- Use a failed or tight case to derive the object. Reject a lemma that hides the parent theorem.")
    print("- If no kernel emerges, identify the missing premise or representation; do not expand a generic sketch.")


def print_discovery() -> None:
    print("\nDiscovery moves: choose by the obstruction")
    print("- Certificate: derive the conditions that would certify the conclusion, then solve for the simplest feasible object.")
    print("- Local to global: pair an exchange, drift, or local inequality with a valid induction, convexity, envelope, or closure argument.")
    print("- Equality: use binding and boundary conditions to determine coefficients; factor the exact residual and test an unused case.")
    print("- Failed construction: isolate the operation that breaks closure; derive the extra state or invariant needed to preserve it.")
    print("- Small cases: compare faithful instances to infer one general relation. A surviving pattern still needs proof.")
    print("- Proof migration: transfer an explicit construction or argument only after checking its assumptions and the return to the target.")
    print("- Existing long proof: seek a shared relation behind a costly block, then prove a replacement without that block.")


def print_controls() -> None:
    print("\nProject controls: use only where needed")
    print("- Unknown answer: fix the admissible object and evaluator; separate witness validity, completeness, optimality, and novelty. Restating the defining property is not an answer.")
    print("- Retry: retain the checked prefix and exact failure; require a new ingredient that addresses it. Renaming a route is not progress.")
    print("- Representation: prove the needed map and recovery implication. Arbitrary substitution requires the relevant range coverage.")
    print("- Retrieval: obtain one applicable premise or proof move; verify source definitions and assumptions. Search rank is not evidence.")
    print("- Tools: state the local question, expected artifact, and implication back before a call. A local check does not prove the parent.")
    print("- Verification: reserve time for boundaries and full assembly. Model agreement, finite non-failure, and strategy scores have proof_effect=none.")
    print("- Scheduling: compare strategies only if route selection is itself failing, on the same problem state and resource grant.")
    print("- Stop: report the exact unresolved relation when another attempt would repeat the same obstruction.")


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
