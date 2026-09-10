# Math Research

[![Codex Skill](https://img.shields.io/badge/Codex-skill-111827?logo=openai&logoColor=white)](SKILL.md)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#development)
[![MIT License](https://img.shields.io/badge/License-MIT-2EA44F.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/jmf-enigma/math-research?style=social)](https://github.com/jmf-enigma/math-research/stargazers)

[Quick start](#quick-start) · [Design](#design) · [Research](#research-basis) · [Evidence](#evidence-boundary) · [中文](#数学研究与证明)

**A mathematics-first Codex skill and bounded proof runner for hard, stuck, or unknown-answer theoretical problems.**

Math Research targets OR/MS, dynamic programming, mechanism design, economics, optimization, learning theory, bandits, games, lower bounds, and probabilistic constructions. It helps Codex find a proof idea, test a claim, use retrieval or mathematical tools, recover from a failed route, and report the strongest status actually supported by evidence.

The default behavior is deliberately small:

1. preserve the exact theorem;
2. find one central object and one nonroutine proof kernel;
3. carry one motivated route end to end;
4. escalate only the first exact obstruction;
5. send complete candidates to a fresh-context referee;
6. repair once, replan, or stop honestly.

Complex route portfolios, lemma graphs, literature-frontier audits, Lean handoffs, and durable ledgers remain available in project mode. They are not the default way to think about a theorem.

## Quick Start

Ask Codex to install the repository-root skill:

```text
Use $skill-installer to install
https://github.com/jmf-enigma/math-research
as math-research.
```

Or clone it manually:

```bash
git clone https://github.com/jmf-enigma/math-research.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/math-research"
```

Restart Codex or refresh skill discovery. The controller uses Python 3.10+ and the standard library. Wolfram, Lean, Sage, Z3, Peppy, Matlas, TheoremSearch, and expert-model consultation are optional backends.

Upgrading from `codex-theory-proof-workbench` or the `theory-proof-workbench` skill? Back up the old installation, install under `math-research`, and update saved commands and skill references. Keep one discoverable `SKILL.md`; existing proof projects retain their files and history. See [migration details](references/runtime-recovery.md#skill-rename).

Invoke it explicitly for a hard proof:

```text
Use $math-research. First look for one natural proof mechanism. Do not
open a full proof project unless the direct route reaches a precise obstruction.
```

## Design

### Natural lane

The active proof context asks three questions: why the claim may be true, what object controls it, and what the first nonroutine implication is. Auxiliary lemmas must be motivated, consumed by the route, and simplify the parent target.

### Adaptive escalation

Only a named obstruction activates a specialist capability.

| Obstruction | Capability |
| --- | --- |
| Suspect claim | Small counterexample or boundary search |
| Missing central object | Tight-case, failure-world, representation, or retrieval lens |
| Local algebra | Wolfram or SymPy exact check |
| Finite leaf | Python, Z3, Sage, NetworkX, or optimization certificate |
| Missing premise | Matlas or TheoremSearch, followed by source verification |
| Stable fragile lemma | Focused Lean handoff |
| Stuck idea-level kernel | One bounded expert consultation, when an approved provider is available |
| Complete proof | Fresh-context natural-language referee |

Expert consultation is an optional search step, not verification. The workbench sends one compact local obstruction and accepts at most one useful follow-up; every returned idea remains `proof_effect=none` until independently reconstructed or checked. [Rosetta](https://github.com/SyntaxSmith/rosetta) can expose ChatGPT Pro as an MCP tool, but it is an unofficial browser bridge and is neither bundled nor required. Review the provider's current terms before use; browser bridges require per-task opt-in and must stop on any rate limit or account restriction.

### Executable loop

For an authorized, self-contained problem, `proof_loop.py` creates a minimal project and runs a bounded generator-referee loop:

```bash
python3 scripts/proof_loop.py path/to/project \
  --claim "EXACT CLAIM" \
  --max-iterations 3 \
  --reasoning-effort high
```

The generator receives a compact packet and works on one route. A complete proof or explicit counterexample is checked in a separate ephemeral Codex context. One local repair is allowed per route; a failed repair or a broken central mechanism triggers replanning. Duplicate scout routes are merged without becoming failure evidence. The loop stops on referee acceptance, a precise request for external evidence, or its iteration/wall-time budget.

Use `--prepare-only` to inspect the first packet without invoking another model. Use `--allow-search` only for public or safely abstracted mathematics; it permits one search turn only after the generator names retrieval as the current obstruction. Add checked project-local evidence with `--reference path/to/artifact` and resume the same project.

Execution resumes from a checkpoint: theorem and acceptance-contract identity, selected plan, pending repair or verification, first error, and reference hashes survive budget boundaries. A waiting run makes no new model call until evidence arrives or its contract changes. Completed results require matching candidate, referee packet, report, and reference hashes; changed obligations trigger review again. Failed routes are hard exclusions only under the same acceptance obligations; older failures remain search hints. See [recovery and migration](references/runtime-recovery.md).

The default reasoning effort is `high`. Reserve `--reasoning-effort max` for a genuinely hard kernel. Iteration and wall-time limits still bound the run.

### Hard exploration after failure

Use this only after two genuinely different routes fail, or after a serious attempt still cannot identify a central object or conditional assembly:

```bash
python3 scripts/proof_loop.py path/to/project \
  --hard-exploration \
  --max-iterations 3 \
  --max-wall-seconds 3600 \
  --reasoning-effort high
```

This adds at most two independent route scouts and one fresh plan selector before the ordinary loop. Scouts do not see one another. The selector can choose only a supplied route and marks the key original step that deserves the proof budget. It schedules work and never counts as proof verification.

Unselected but viable routes remain in a three-item history. The controller removes exact route-signature repeats against the full history, while a recent detailed failure window helps scouts and the selector reject semantic renamings. Automatic semantic deduplication is not perfect. The hard pass stops before proof generation when no route clears the assembly gate or when one named external capability is required.

### Durable project mode

Use the larger project harness only for multi-session, multi-lemma, tool-heavy, or repeatedly failed work:

```bash
python3 scripts/start_proof.py --title "short-name" --claim "EXACT CLAIM"
python3 scripts/proof_doctor.py path/to/project
python3 scripts/proof_runtime.py brief path/to/project --markdown
```

It preserves failed-state fingerprints, decomposition and parent-replay evidence, computation artifacts, verifier reports, Lean handoffs, and honest proof status.

## Research Basis

The runtime is a conservative synthesis, not a reproduction of any one proof system. [Rethlas](https://arxiv.org/abs/2604.03789) informs adaptive stage choice. [QED](https://arxiv.org/abs/2604.24021) informs stable planning, key-step attention, and proof-versus-plan failure diagnosis. [Aletheia](https://arxiv.org/abs/2602.10177) and verifier studies inform bounded generation, abstention, and cold review. The [sum-product agent](https://arxiv.org/abs/2607.20525) motivates developing a precise plan before long construction. [Beyond the Frontier](https://arxiv.org/abs/2605.25143) motivates preserving plausible historical routes.

Each mechanism passes a stage, evidence, dependency, transfer, and regression-test audit before entering the skill. The workbench does not claim those papers' private models, learned verifiers, process reward models, token-prefix search, hardware, or reported success rates. The [September 2026 update](references/ai-math-workflows-2026.md) integrates FLARE, MechGeo, AlphaProof Nexus, and AI-assisted Banach-space and Ramsey work: concrete representation maps, counterexample scope, and failed-closure-driven invariant discovery. These are conditional mathematical moves, not a larger mandatory pipeline. See the earlier [source-to-control audit](references/research-backed-proof-loop.md).

## Evidence Boundary

- Retrieval returns theorem candidates, not authority. Check the source, definitions, and assumptions.
- Simulation and bounded search guide or refute; absence of a witness is not proof.
- CAS and solver outputs support only their exact encoded claim and assumptions.
- A natural-language referee reduces anchoring but is not formal verification.
- A Lean kernel checks the formal statement it receives; fidelity and final assembly still matter.

The workbench separates the mathematical outcome, evidence basis, and scope. Model acceptance is `referee-accepted`, with proof/refutation disposition and explicit human/formal-check flags. It does not automatically mean `human-proof` or a certified refutation. Legacy labels remain readable; `counterexample-tested` only means that a bounded search found no witness. See the [conditional verification checks](references/verification-gate.md).

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

The smoke suite checks infrastructure and control behavior. It is not evidence that the system solves unseen research problems. Meaningful capability claims require held-out, same-model, same-budget proof evaluations. The [evaluation protocol](references/evaluation.md) separates controller fixtures, mathematical forward tests, and comparative capability evidence.

Released under the [MIT License](LICENSE).

---

# 数学研究与证明

[快速开始](#快速开始) · [设计](#设计) · [研究依据](#研究依据) · [证据边界](#证据边界) · [English](#math-research)

**一个以数学思考为默认入口、带有有界证明运行器的 Codex skill，面向困难、卡住或答案尚不明确的理论问题。**

Math Research 主要覆盖 OR/MS、动态规划、机制设计、经济理论、优化、learning theory、bandits、博弈、lower bounds 和概率构造。它帮助 Codex 寻找证明机制、检验命题、调用检索或数学工具、恢复失败路线，并只报告证据真正支持的结论。

默认流程只有六步：

1. 保持原命题准确不变；
2. 找到一个中心对象和一个关键 proof kernel；
3. 沿一条有数学动机的路线走到底；
4. 只升级第一个准确障碍；
5. 把完整候选交给独立新上下文 referee；
6. 局部修复一次，然后重新规划或诚实停止。

路线组合、lemma graph、文献 frontier、Lean handoff 和完整 ledger 都保留在项目模式中，但不再侵入普通证明的第一轮思考。

## 快速开始

让 Codex 安装仓库根目录中的 skill：

```text
使用 $skill-installer 安装
https://github.com/jmf-enigma/math-research
安装名称使用 math-research。
```

显式调用：

```text
使用 $math-research。先寻找一条自然的证明机制，只有直接路线
出现准确障碍时才启动复杂项目模式。
```

核心只依赖 Python 3.10+ 标准库。Wolfram、Lean、Sage、Z3、Peppy、Matlas、TheoremSearch 和专家模型咨询都是按需后端。

旧版用户请先备份安装目录，再以 `math-research` 安装并更新调用名称。已有证明项目和历史可以继续使用；迁移后只保留一个可被发现的 `SKILL.md`。详见[改名迁移](references/runtime-recovery.md#skill-rename)。

## 设计

### 自然证明通道

第一轮只问三个数学问题：命题为什么可能为真，什么对象控制结论，以及第一个真正不平凡的推理是什么。辅助引理必须有明确来源、会被后续路线使用，并使 parent target 严格变简单。

### 按障碍升级

命题可疑时寻找最小反例；中心对象缺失时使用紧例、失败世界、表示变换或定理检索；局部代数交给 Wolfram/SymPy；有限结构交给 Python、Z3 或 Sage；稳定但脆弱的 lemma 才交给 Lean；完整候选才进入独立 referee。只有准确的 idea-level kernel 被局部方法卡住时，才允许做一次有界专家咨询。咨询结果只是候选思路，必须重新推导或验证。Rosetta 可以把 ChatGPT Pro 暴露为 MCP 工具，但它是可选的非官方浏览器桥，本仓库不会捆绑安装；使用前需要确认当前服务条款并对本次任务单独同意，遇到限流或账户限制立即停止。

### 可执行闭环

```bash
python3 scripts/proof_loop.py path/to/project \
  --claim "准确命题" \
  --max-iterations 3 \
  --reasoning-effort high
```

runner 会创建最小项目，每轮只向 generator 提供紧凑 packet。完整证明或显式反例由新的临时 Codex 上下文检查。每条路线最多局部修复一次，修复失败或中心机制失效后重新规划；scout 提出重复路线只会去重，不会因此记为失败。达到验证接受、明确需要外部证据、迭代上限或时间上限时停止。

`--prepare-only` 只准备 packet，不调用另一个模型。只有公开或安全抽象后的数学问题才使用 `--allow-search`；它不会预先打开搜索，只有 generator 明确把 retrieval 识别为当前障碍后，才允许下一轮检索一次。外部工具产生的证据保存在项目内，再通过 `--reference` 送入下一轮。

默认 reasoning effort 为 `high`。只有确认遇到困难 proof kernel 时才升到 `--reasoning-effort max`。迭代和时间上限仍然生效。

### 失败后的困难探索

只有两条实质不同的路线都失败，或者认真尝试后仍找不到中心对象或完整组装关系时，才使用：

```bash
python3 scripts/proof_loop.py path/to/project \
  --hard-exploration \
  --max-iterations 3 \
  --max-wall-seconds 3600 \
  --reasoning-effort high
```

困难探索最多让两个互不读取彼此答案的 scout 提出路线，再由一个新上下文只从现有候选中锁定计划，并标出真正值得投入证明预算的关键原创步骤。selector 只负责调度，不构成证明验证。

未选中但仍合理的路线最多保留三条。控制器会在完整历史中排除完全相同的路线指纹，并把近期失败细节送给 scout 和 selector，用来识别只是换了说法的旧路线；自动语义去重仍不是完美的。没有路线通过 assembly gate，或者需要一种明确外部能力时，困难探索会在生成长证明前停止。

### 长期项目模式

跨对话、多 lemma、多工具或已经反复失败的问题，可以使用 `start_proof.py`、`proof_doctor.py` 和 `proof_runtime.py`。复杂状态机只在这里启用，用来保存失败指纹、parent replay、计算证据、referee 报告和 Lean handoff。

## 研究依据

[2026 年 9 月更新](references/ai-math-workflows-2026.md) 核对了 FLARE、MechGeo、AlphaProof Nexus、Banach 空间和 Ramsey 研究中的 AI 用法。对应修改包括：用具体映射说明换元或重构为何有效；区分原命题、辅助引理和编码的反例；从失败的封闭性条件中寻找新不变量；保存中断前真正待做的数学动作。文献方法、作者报告的结果和本工具实际实现的能力分别标注。

当前运行逻辑是多项研究的克制组合，并不是对某个系统的复刻。[Rethlas](https://arxiv.org/abs/2604.03789) 主要支持按障碍选择阶段。[QED](https://arxiv.org/abs/2604.24021) 支持先稳定计划、明确关键原创步骤，并区分证明执行失败与计划失败。[Aletheia](https://arxiv.org/abs/2602.10177) 及 verifier 研究支持有界生成、允许不确定和独立冷审查。[sum-product agent](https://arxiv.org/abs/2607.20525) 支持先把计划与缺口想清楚，再投入长证明。[Beyond the Frontier](https://arxiv.org/abs/2605.25143) 支持保留尚未证伪的历史路线。

每项机制进入 skill 前都要检查它改善的是哪个阶段、证据强度如何、依赖哪些不可用系统、能够迁移成什么动作，以及怎样做回归测试。本项目不声称拥有这些论文的私有模型、learned verifier、process reward model、逐 token 搜索、硬件或论文报告的成功率。完整记录见 [source-to-control audit](references/research-backed-proof-loop.md)。

证明运行器保留所选计划、待修复候选、待验证证明和第一处错误。预算用尽后继续原任务；等待证据时重复运行不会重新调用模型。验收要求变化会触发重新复核，通过的文件必须与 referee 实际读取的材料一致。命题修改后保留历史，但旧路线的失败记录不再自动约束新命题。详见[恢复与迁移说明](references/runtime-recovery.md)。

## 证据边界

- 检索结果只是候选，必须核查原文、定义和假设。
- 模拟和有限搜索可以提示或反驳，找不到反例不能证明命题。
- CAS 与 solver 只支持实际编码的局部命题。
- 自然语言 referee 可以减少锚定，但不是形式证明。
- Lean 检查收到的形式命题，仍需核查语义一致性与最终组装。

现在分别记录数学结论、证据依据和适用范围。模型审稿通过记为 `referee-accepted`，另记候选是证明还是反驳，以及是否经过人工或形式化检查；不会自动升级成已核验的定理或反例。旧状态仍可读取，`counterexample-tested` 仍只表示有限搜索未找到反例。检查流程改为四项核心检查，加上由当前证明触发的专项检查。

回归测试验证基础设施和控制逻辑，并不证明系统已经更擅长解决未见研究难题。真正的能力提升需要在相同模型和预算下进行 held-out 对照测试。

本仓库使用 [MIT License](LICENSE)。
