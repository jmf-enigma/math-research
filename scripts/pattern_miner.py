#!/usr/bin/env python3
"""Mine lightweight pattern guesses from exact small-case sequences."""

from __future__ import annotations

import argparse
from fractions import Fraction


def parse_fraction(text: str) -> Fraction:
    return Fraction(text.strip())


def parse_sequence(text: str) -> list[Fraction]:
    values = [parse_fraction(part) for part in text.replace(";", ",").split(",") if part.strip()]
    if len(values) < 2:
        raise SystemExit("provide at least two sequence values")
    return values


def fmt(x: Fraction) -> str:
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"


def differences(values: list[Fraction]) -> list[list[Fraction]]:
    rows = [values]
    while len(rows[-1]) > 1:
        prev = rows[-1]
        rows.append([prev[i + 1] - prev[i] for i in range(len(prev) - 1)])
    return rows


def constant_row_index(rows: list[list[Fraction]]) -> int | None:
    for idx, row in enumerate(rows[1:], start=1):
        if len(row) >= 2 and all(item == row[0] for item in row):
            return idx
    return None


def ratios(values: list[Fraction]) -> list[Fraction] | None:
    if any(v == 0 for v in values[:-1]):
        return None
    return [values[i + 1] / values[i] for i in range(len(values) - 1)]


def binom_expr(rows: list[list[Fraction]], start: int, upto: int | None = None) -> str:
    if upto is None:
        upto = len(rows)
    terms = []
    for k, row in enumerate(rows[:upto]):
        coeff = row[0]
        if coeff == 0:
            continue
        if k == 0:
            terms.append(fmt(coeff))
        elif k == 1:
            terms.append(f"{fmt(coeff)}*C(n-{start},1)")
        else:
            terms.append(f"{fmt(coeff)}*C(n-{start},{k})")
    return " + ".join(terms) if terms else "0"


def predict_next(rows: list[list[Fraction]]) -> Fraction:
    return sum(row[-1] for row in rows)


def polynomial_holdout(values: list[Fraction], start: int) -> str | None:
    if len(values) < 5:
        return None
    train = values[:-1]
    holdout = values[-1]
    rows = differences(train)
    const_idx = constant_row_index(rows)
    predicted = predict_next(rows if const_idx is None else rows[: const_idx + 1])
    n_holdout = start + len(values) - 1
    status = "pass" if predicted == holdout else "fail"
    return f"polynomial holdout n={n_holdout}: predicted {fmt(predicted)}, actual {fmt(holdout)} ({status})"


def geometric_holdout(values: list[Fraction], start: int) -> str | None:
    if len(values) < 5:
        return None
    train = values[:-1]
    ratio_values = ratios(train)
    if not ratio_values or not all(value == ratio_values[0] for value in ratio_values):
        return None
    holdout = values[-1]
    predicted = train[-1] * ratio_values[0]
    n_holdout = start + len(values) - 1
    status = "pass" if predicted == holdout else "fail"
    return f"geometric holdout n={n_holdout}: predicted {fmt(predicted)}, actual {fmt(holdout)} ({status})"


def print_analysis(values: list[Fraction], start: int) -> None:
    rows = differences(values)
    print("values")
    print("- " + ", ".join(fmt(v) for v in values))
    print("finite differences")
    for idx, row in enumerate(rows[:6]):
        label = "value" if idx == 0 else f"diff {idx}"
        print(f"- {label}: " + ", ".join(fmt(v) for v in row))
    const_idx = constant_row_index(rows)
    if const_idx is not None:
        print("polynomial guess")
        print(f"- finite differences stabilize at order {const_idx}")
        print(f"- binomial/Newton form: f(n) = {binom_expr(rows, start, const_idx + 1)}")
    else:
        print("polynomial guess")
        print("- no low-order constant finite difference found in supplied values")
        print(f"- interpolating binomial form: f(n) = {binom_expr(rows, start)}")
    ratio_values = ratios(values)
    if ratio_values:
        print("ratio check")
        print("- " + ", ".join(fmt(v) for v in ratio_values))
        if all(v == ratio_values[0] for v in ratio_values):
            print(f"- geometric guess with ratio {fmt(ratio_values[0])}")
    holdouts = [item for item in [polynomial_holdout(values, start), geometric_holdout(values, start)] if item]
    if holdouts:
        print("holdout")
        for holdout in holdouts:
            print(f"- {holdout}")
    print("proof-use hints")
    print("- If differences stabilize, try induction or telescoping on the last nonconstant difference.")
    print("- If ratios stabilize, try multiplicative potential, log transform, or change of measure.")
    print("- A holdout supports selecting a conjecture; promotion to a theorem requires a proof at the claimed scope.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seq", required=True, help="Comma-separated exact values, e.g. '1,4,9,16,25'")
    parser.add_argument("--start", type=int, default=1, help="Index of the first value, default 1")
    args = parser.parse_args()
    print_analysis(parse_sequence(args.seq), args.start)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
