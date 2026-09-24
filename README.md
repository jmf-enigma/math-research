# Math Research

[中文](#数学研究与证明) · [Install](#install) · [Design](#design) · [Development](#development)

A skill for discovering, repairing, refuting, and structurally simplifying mathematical proofs. It targets hard or unknown-answer problems in OR/MS, optimization, probability, learning, games, and economic theory.

The deliverable is mathematics: a complete argument, a valid counterexample, or the exact unresolved implication. The workflow centers on a controlling object and a kernel that actually closes the target. Computation, retrieval, formalization, and project tracking serve that argument.

## Install

Ask your agent:

```text
Use $skill-installer to install https://github.com/jmf-enigma/math-research
as math-research.
```

Then invoke it:

```text
Use $math-research to solve this theorem. Find the controlling mechanism,
carry the argument through, and state exactly what remains unproved.
```

For an existing proof:

```text
Use $math-research to find a structural replacement for this long proof.
Preserve the theorem and show which calculations the new argument removes.
```

Core scripts require Python 3.10+ and its standard library. The optional agent runner also needs an available Codex CLI. Mathematical tools and specialist skills are optional; use those installed in your environment. See [migration](references/runtime-recovery.md#skill-rename) for the former `theory-proof-workbench` name.

## Design

[SKILL.md](SKILL.md) is the entrypoint. It makes four decisions:

1. **Target:** what exact statement must survive, including boundaries and quantifiers?
2. **Mechanism:** which nonroutine implication controls the conclusion, and how does it close the whole argument?
3. **Obstruction:** what premise, construction, identity, or witness would settle the first failed step?
4. **Evidence:** what has actually been proved or checked, and does it cover the original theorem?

Reference files supply specific methods only when needed. Use [discovery](references/proof-idea-generator.md) for a missing object, [structural compression](references/structural-proof-compression.md) for a replacement proof, and the [domain router](references/proof-router.md) for a relevant mathematical playbook. A fixed proof with clearer prose belongs to `math-proof-writing`.

Structural simplification must reduce mathematical obligations. A shared budget, recurrence, potential, or symmetry can replace many calculations; simply naming the old calculation does not. Keep the valid old proof until the replacement covers the same claim and downstream uses.

### Optional execution

```bash
python3 scripts/proof_loop.py path/to/project \
  --claim "EXACT CLAIM" --max-iterations 3 --reasoning-effort high
```

The bounded runner separates generation from review, permits one local repair per route, and preserves pending work across runs. A model-accepted result is `referee-accepted`, with proof/refutation disposition and evidence scope; it does not assert formal or human verification.

Use `--prepare-only` to inspect the next packet. Supply checked project-local evidence with `--reference`. Search, hard exploration, theorem revisions, damaged checkpoints, and the larger project mode are documented in [runtime recovery](references/runtime-recovery.md).

### Evidence and sources

A numerical pattern remains conjectural. A tool proves only its encoded claim; a local lemma needs an assembly argument. A counterexample must satisfy the original assumptions. See [verification](references/verification-gate.md) and [evaluation](references/evaluation.md).

The [research map](references/research-backed-proof-loop.md) records source mechanisms and limitations; the [September update](references/ai-math-workflows-2026.md) preserves versioned source checks. These are maintenance references. The skill does not acquire a paper's private models, training, compute, or reported success rate by citing it.

For eligible algorithmic performance problems, the [Peppy bridge](references/peppy-proof-bridge.md) uses the companion Peppy workflow and separate [PEPFlow project](https://github.com/pepflow-lib/PEPFlow). Credit Peppy, PEPFlow, and the relevant PEP/interpolation methodology when materially used. The bridge is a routing layer, not an independent implementation of those methods.

## Development

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
PYTHONPYCACHEPREFIX=/tmp/codex-pycache python3 -m py_compile scripts/*.py
python3 scripts/smoke_proof_loop.py
python3 scripts/test_proof_loop_recovery.py
python3 scripts/test_attempt_matching.py
python3 scripts/test_computation_scope.py
python3 scripts/test_evidence_lifecycle.py
python3 scripts/smoke_workbench.py
```

Regression tests check executable behavior and artifact integrity. Mathematical forward tests need an independent solver given a raw task, followed by separate review. Improved performance on unseen research problems requires matched comparisons; neither passing tests nor shorter instructions establishes it.

Released under the [MIT License](LICENSE).

---

# 数学研究与证明

Math Research 用于发现、修复、反驳和结构性简化数学证明，重点覆盖 OR/MS、优化、概率、学习、博弈与经济理论。

核心是找到控制结论的数学对象，证明关键关系，再完成原命题的全部推导。遇到障碍时，先说清哪一步缺少什么，再决定检索、计算或形式化。交付完整证明、有效反例，或一个准确的未解问题。

## 快速开始

```text
使用 $skill-installer 安装
https://github.com/jmf-enigma/math-research
名称为 math-research。
```

```text
使用 $math-research 处理这个定理。找到真正控制结论的机制，
完成全部推导，并准确说明仍未证明的部分。
```

对于已有长证明：

```text
使用 $math-research 寻找结构性替代证明。保持原命题，
说明新机制为什么成立，以及真正省去了哪些计算和分类。
```

[主文件](SKILL.md)负责目标、机制、障碍、证据四个判断；[具体方法](references/proof-router.md)按需读取。只改变表达、不改变数学路线时，使用 `math-proof-writing`。

## 结构简化

先倒查结论真正需要什么，再从旧证明中提炼共享约束、递推、势函数、对称性或其他统一关系。替代证明必须覆盖相同边界和下游用途；新定义与残留计算也计入成本。原有效证明保留到替代完成。

## 执行与检查

短证明直接处理。多轮任务可使用上面的有界运行器；它保存当前命题、证据、失败位置和待执行动作，支持中断后继续。具体操作见[执行与恢复](references/runtime-recovery.md)，旧名称迁移也在该页。

数值规律、局部工具结果、完整数学证明与形式化验证分别报告。证明正确但没有完成所要求的简化时，继续寻找替代路线，不把原命题判错。程序测试通过只说明相应执行行为通过检查；数学能力与研究新颖性需要另外评价。
