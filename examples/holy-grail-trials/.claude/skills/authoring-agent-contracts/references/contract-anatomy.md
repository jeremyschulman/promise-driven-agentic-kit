# Contract anatomy reference

The exact structure of both contract-document types, the Promise Theory
vocabulary, and a validation-error → fix table. This mirrors the XSD schemas
(`schema/agent-contract.xsd`, `schema/agent-manifest.xsd`, `schema/promise-common.xsd`),
which are themselves annotated and worth reading for the authoritative rules.

## Contents

- [LLM agent — `agent_*.xml`](#llm-agent--agent_xml)
- [Non-LLM agent — `manifest_*.xml`](#non-llm-agent--manifest_xml)
- [The `<fizzbee>` element](#the-fizzbee-element)
- [The Promise Theory manifest](#the-promise-theory-manifest)
- [The promise `type` vocabulary](#the-promise-type-vocabulary)
- [Conditions and quenching](#conditions-and-quenching)
- [Validation error → fix](#validation-error--fix)

## LLM agent — `agent_*.xml`

Root `<agent-instructions>` with required attributes `workflow` (the stable id;
matches the `agent_<workflow>.xml` filename) and `version` (dotted, e.g. `1.0`).
Children, in this exact order, all required:

The **agent contract** is the whole XML artifact. `<verifiable-behavior>` is the
specific section containing its exhaustively checkable behavior model.

```xml
<agent-instructions workflow="barista" version="1.0">
  <objective> … prose … </objective>
  <verifiable-behavior>
    <fizzbee mode="runtime-instructions" verified="fizz-0.5.1"> … </fizzbee>
  </verifiable-behavior>
  <promises> … description, tools, offers, uses … </promises>
  <step-guidance action="ActionName"> … prose … </step-guidance>   <!-- 1 or more -->
  <enforcement> … <rule id="…">…</rule> … </enforcement>
  <responses> … named templates … </responses>
</agent-instructions>
```

- `<step-guidance>` — one per action; requires an `action` attribute. The interior is
  free-form prose (the schema treats it as a lax wildcard) — use whatever sub-elements
  read best (`binding`, `note`, `gate`, `render`, …). The `action` label usually matches
  a FizzBee action, but need not (some steps are pure LLM-judgment stages).
- `<enforcement>` — a short descriptive lead-in plus one `<rule id="…">` per
  code-enforced invariant. Match `id` to the FizzBee `always assertion` name.
- `<responses>` — named template elements (open content); text may contain Markdown and
  `[placeholder]` tokens.

## Non-LLM agent — `manifest_*.xml`

Root `<agent-manifest>` with required attributes `agent` (the name other agents
reference in `to`/`from`) and `version`. Just two children:

```xml
<agent-manifest agent="espresso_machine" version="1.0">
  <description> … prose … </description>
  <promises> … offers, uses … </promises>
</agent-manifest>
```

Note the shape difference from an LLM contract: here `<description>` sits at the **root**;
in an LLM contract it lives **inside** `<promises>` (alongside `<tools>`).

## The `<fizzbee>` element

- `mode` — **required, fixed** to `runtime-instructions`. This is the dual-reading trick:
  `oneof` = "explore all branches" (checker) and "pick exactly one" (LLM).
- `verified` — optional; records the fizz toolchain version last used to certify the
  block (e.g. `fizz-0.5.1`). Stamp it once the contract model-checks clean.
- The text content is raw FizzBee (YAML frontmatter + actions/guards/invariants). It is
  opaque to the schema by design — the `fizz` model checker validates it, not the XSD.

## The Promise Theory manifest

Inside `<promises>`:

**LLM contract** order: `<description>`, `<tools>`, one-or-more `<offer>`, then any `<use>`.
**Manifest** order: one-or-more `<offer>`, then any `<use>`. (No `description`/`tools` here.)

```xml
<offer id="serve_drink" type="workflow" to="customer">
  <body>What the agent promises to do.</body>
  <condition ref="payment_confirmed"/>          <!-- 0 or more -->
</offer>

<use id="brew_drink" from="espresso_machine" quenches="drink_ready">
  <body>What the agent accepts from another agent.</body>
</use>

<tools>
  <tool name="take_order"/>                      <!-- names must resolve to real callables -->
</tools>
```

- `<offer>` attributes: `id` (required), `type` (required, from the vocabulary below),
  `to` (required, space-separated promisees), `entailed-by` (optional; on a superagent's
  exterior offers, names the interior offer ids that justify it).
- `<use>` attributes: `id` (required), `from` (required, single providing agent),
  `quenches` (optional, space-separated condition refs it satisfies).
- `<condition>` attributes: `ref` (required), `assessed` (optional, only value `self`).

## The promise `type` vocabulary

The `type` attribute on `<offer>` is a controlled enumeration — a typo fails validation.
The categories are generic Promise Theory roles (not domain nouns), so they carry across
systems:

| `type` | Meaning |
| --- | --- |
| `workflow` | a multi-step capability the agent performs on request |
| `invariant` | a guarantee the agent always keeps regardless of input (usually code-backed) |
| `session-state` | shared, persisted state the agent publishes for others to read |
| `auth` | an authenticated session / credential the agent vends |
| `identity` | a verified principal (who a request is from) |
| `receipts` | staged binary artifacts (files) made available downstream |
| `ocr` | a best-effort extraction/interpretation result (explicitly non-authoritative) |
| `ux` | a user-facing surface: progress, a final reply, rendered output |
| `card` | exterior catalog/advertising text (what the outside world sees) |

If your system genuinely needs a new category, extend the enumeration in
`schema/promise-common.xsd` deliberately — don't smuggle a domain noun into `type`.

## Conditions and quenching

A condition is a dependency stated without breaking agent autonomy: "I promise `b`
*given* `c`." Each condition on an offer must resolve one of two ways:

1. **Quenched by another agent** — some agent publishes `<use … quenches="c">`, i.e. it
   promises to acquire `c`. The promise-graph verifier follows this edge from need to
   provider.
2. **Self-assessed** — `<condition ref="c" assessed="self"/>` means the promiser evaluates
   `c` itself; no external offer is required.

An unquenched, non-self-assessed condition is a **design defect the verifier reports** —
that is the whole value: a dependency nobody agreed to provide is caught before runtime.

## Validation error → fix

| Error (source) | Fix |
| --- | --- |
| `'foo' is not an element of the set {workflow, invariant, …}` (xmllint) | Use a valid `type`; extend the enum only if a real new category |
| `Missing child element(s). Expected is ( step-guidance )` (xmllint) | Add the missing required section; LLM contracts need all six |
| `attribute 'from' is required but missing` (xmllint) | Every `<use>` needs `from`; every `<offer>` needs `id`/`type`/`to` |
| `<fizzbee mode> is '…', expected 'runtime-instructions'` (loader) | Set `mode="runtime-instructions"` |
| `condition 'c' is not quenched by any use` (promise-graph) | Add a `use … quenches="c"` or mark `assessed="self"` |
| `uses 'x' which 'Y' does not offer` (promise-graph) | Fix the `id`/`from`, or add the matching `<offer>` to agent Y |
| `uses 'x' from unknown agent 'Z'` (promise-graph) | `Z` has no manifest and isn't a declared external party; add its manifest or register it as external |
| model check FAILS with a trace (fizz) | Read the step sequence to the bad state; tighten a guard. Never weaken the invariant just to pass |
