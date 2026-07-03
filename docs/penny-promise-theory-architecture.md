# Penny as a System of Promising Agents

> _Reproduced from the Penny reference implementation. File paths and code references below point into Penny's source tree, which is not part of this kit._


**An architecture proposal reframing the Penny expense agent using Promise Theory**

*Grounded in the Penny source tree (`penny/`) and in Bergstra & Burgess, "Promise Theory: Principles and Applications" (2nd ed.), plus the accompanying reference papers.*

---

## Phase 1 — Current Architecture Analysis

### 1.1 The agent inventory

Penny is a multi-agent system for SAP Concur expense workflows, fronted by Gemini Enterprise (GE) over the A2A protocol. The agents, as they exist in code today:

| # | Agent | Kind | Lives in |
|---|-------|------|----------|
| 1 | **`penny_orchestrator`** | ADK `LlmAgent` (root) | `src/penny/a2a/workflows/orchestrator.py` → `build_orchestrator_agent()` |
| 2 | **`penny_create_expense_report`** | ADK `LlmAgent` (subagent) | `src/penny/a2a/workflows/create_expense_report.py` → `build_create_expense_report_agent()` |
| 3 | **`penny_add_expense`** | ADK `LlmAgent` (subagent) | `src/penny/a2a/workflows/add_expense.py` → `build_add_expense_agent()` |
| 4 | **`ExpenseAgentExecutor`** | A2A protocol executor (non-LLM) | `src/penny/agent/executor.py` |
| 5 | **Receipt OCR service** | Gemini-vision call (non-conversational model agent) | `src/penny/expense_core/services/receipt_extraction.py` → `extract_receipt()` |
| 6 | **Executive Assistant MCP server** (legacy, dead-ended) | FastMCP server | `src/penny/mcp_servers/executive_assistant/server.py` |
| 7 | **Receipt Intake A2A agent** (legacy, superseded) | A2A executor | documented in `docs/RECEIPT_INTAKE_A2A.md`; spike survivor `src/penny/a2a_spike/executor.py` (`FilePartEchoExecutor`) |
| 8 | **Gemini Enterprise** | External client/orchestrator | not in repo; interfaces via `src/penny/agent/server.py` (`/a2a`) |
| 9 | **SAP Concur** | External service | accessed via `src/concur_client/` (`AsyncConcurClient`) |

Supporting non-agent infrastructure that carries state between agents: `EaMcpRuntime` / `EaSessionManager` (`src/penny/expense_core/runtime.py`), `EaSessionStore` (Firestore via Mongo API, `src/penny/expense_core/session_store.py`), `GcsReceiptStore` (`src/penny/receipts/gcs_store.py`), `FirestoreAdkSessionService` (`src/penny/agent/session_service.py`), and `EaOAuthCoordinator` (`src/penny/expense_core/oauth.py`).

### 1.2 What each agent does, depends on, and how it communicates

**`penny_orchestrator`** — the root of every request. Its instruction is the *entire XML contract document* `agent_contracts/agent_orchestrator.xml`, loaded verbatim by `ContractDoc.instruction_text` (`src/penny/a2a/workflows/contract_doc.py`). It authenticates the user with Concur, resolves the active traveler in the EA-delegate scenario, classifies intent (`DetectIntent` in the FizzBee block enumerates `INTENT_CREATE_REPORT`, `INTENT_ADD_EXPENSE`, `INTENT_LIST_REPORTS`, `INTENT_SELECT_REPORT`, `INTENT_MANAGE_TRAVELER`, `INTENT_BANTER`, `INTENT_OUT_OF_SCOPE`), and routes to workflow subagents. It holds fourteen cross-cutting tools (`build_orchestrator_tools()`): session context, traveler delegation (`list_delegators`, `resolve_delegator`, `set_active_traveler`, …), active-report selection (`resolve_active_report`, `set_active_report`, …), Concur OAuth (`connect_concur`, `complete_concur_connection`, `disconnect_concur`), and `list_open_reports`. Its two subagents are wired in at construction: `sub_agents=[build_create_expense_report_agent(), build_add_expense_agent()]` (orchestrator.py line 118).

**`penny_create_expense_report`** — creates one draft Concur report. Instruction is `agent_contracts/agent_create_expense_report.xml`. Its FizzBee contract guards `CreateExpenseReport` with `require business_purpose_confirmed` and `require scenario == "standard" or owner_resolved`, and asserts invariants `CommentIsBoilerplate`, `EventIsDefault`, `CreateRequiresConfirmation`, `CreateRequiresOwner`. Tools (`build_workflow_tools()`): `get_session_context`, `set_active_traveler`, `connect_concur`, `complete_concur_connection`, `create_report_with_contract`. The last calls `penny.expense_core.services.contract.create_contract_report()`, the "code-enforced half" of the contract, which hard-codes `PENNY_REPORT_COMMENT` and the default Event so the LLM cannot vary them.

**`penny_add_expense`** — adds one expense line, receipt-first via OCR. Instruction is `agent_contracts/agent_add_expense.xml`, whose contract gates `CreateExpense` on `report_resolved`, `expense_type_resolved`, `business_purpose_confirmed`, `payment_type_resolved`, and `(not has_receipt) or receipt_readable`, plus a hotel-itemization sub-machine (`ItemizeHotel` requires `all_lines_mapped` and `reconciles`). Tools: `get_session_context`, `get_active_report`, `list_open_reports`, `list_staged_receipts`, `extract_receipt`, `classify_expense`, `create_expense`, `create_expense_with_receipt`. The twelve-type whitelist is code-enforced in `src/penny/expense_core/services/expense_types.py` (`SUPPORTED_EXPENSE_TYPES`, `classify_expense`).

**`ExpenseAgentExecutor`** (`src/penny/agent/executor.py`) — the A2A boundary. Per request it: resolves Google identity from the bearer token (`_resolve_identity` → `GoogleIdentityResolver`, `src/penny/receipts/identity.py`); stages attached receipt bytes into GCS (`self._gcs_store.store(...)`); constructs an `AgentRequestContext` and installs it in a `ContextVar` (`set_request_context`, `src/penny/agent/context.py`); runs the ADK `Runner` over the orchestrator; streams progress frames (`_TOOL_PROGRESS` map) and post-processes replies into A2UI surfaces (`_compose_reply_parts` → `src/penny/a2a/a2ui.py`).

**Receipt OCR service** — `extract_receipt()` in `receipt_extraction.py` sends staged bytes to Gemini vision and returns a structured draft (vendor, date, amount, `lineItems`, `readable` flag). Its module docstring is explicit: "nothing here is authoritative"; `REQUIRED_RECEIPT_FIELDS = ("transactionDate", "vendor", "amount")` defines the readability gate.

**Legacy pair** — the Executive Assistant MCP server (`mcp_servers/executive_assistant/`, ~22 tools over the same `expense_core` services) and the Receipt Intake A2A agent cooperated across process boundaries using the Google `sub` + receipt `sha256` as a shared key in GCS (`docs/RECEIPT_INTAKE_A2A.md`). `docs/AGENT.md` marks this two-connector model as replaced by the unified agent; `src/penny/serve/combined.py` still mounts both behind one URL.

### 1.3 Communication mechanisms

Four distinct mechanisms carry intent between agents today:

1. **A2A JSON-RPC** (GE ↔ Penny): `server.py` registers `/a2a` via `create_jsonrpc_routes(...)`; the executor receives `RequestContext` and enqueues events.
2. **In-process LLM delegation** (orchestrator ↔ subagents): ADK `sub_agents` transfer. The orchestrator's contract says the handoff passes "the full original user message as context" (`RouteToWorkflow` step-guidance) and that after handoff "the orchestrator does not speak again until the subagent returns its result."
3. **Direct function calls** (agents → tools → services): every tool in `src/penny/agent/tools.py` calls straight into `expense_core.services.*`, which call `AsyncConcurClient`.
4. **Shared mutable state** — the load-bearing one:
   - `ContextVar` request context (`agent/context.py`): the executor writes it; every tool reads it via `require_agent_invocation()`.
   - `EaMcpRuntime` + Firestore (`EaStoredToken` fields `active_traveler_login`, `active_report_id`, `active_report_name`, `active_report_url` in `session_store.py`): the orchestrator writes the active traveler and active report; subagents *implicitly consume* them. The orchestrator contract states this outright: "The orchestrator owns set_active_traveler; subagents consume whoever is active" (comment above `ResolveTraveler` in `agent_orchestrator.xml`).
   - GCS receipt store: executor writes receipt bytes; `extract_receipt` / `attach_receipt_to_expense` read them by `(sub, sha256)`.
   - `FirestoreAdkSessionService`: shared conversation history keyed by `(user_id=sub, session_id=context_id)`.

### 1.4 The current control model

The control model is explicitly hierarchical command-and-control at the top, with an unusually promise-friendly substrate underneath.

**Central orchestration, stated as ownership.** `agent_orchestrator.xml` `<objective>`: "The orchestrator owns EVERY turn. Each incoming message is evaluated here before being forwarded to an active subagent or handled directly." The orchestrator decides when subagents run (`RouteToWorkflow`), suspends them (`ConfirmPivot`), resumes them (`ResumeWorkflow`), and completes them (`CompleteWorkflow`). Subagents have no say; they are invoked.

**Implicit obligations through shared state.** Subagent correctness *depends on* the orchestrator having done its job: `penny_create_expense_report`'s `CreateRequiresOwner` invariant depends on a traveler that the *orchestrator* resolved and persisted into `EaMcpRuntime.active_traveler_login`. Nothing in the subagent's interface declares this dependency; tools discover it at call time (`_resolve_active_traveler_email` in `agent/context.py` returns `active_traveler_email_required_response()` when it's missing). That is an obligation imposed by convention, not a negotiated promise.

**Tight coupling at construction.** `build_orchestrator_agent()` imports and instantiates both subagent builders directly; `agent/agent.py` `build_expense_agent()` hard-wires the orchestrator as root. Adding a workflow means editing the orchestrator module.

**Upstream, Penny itself is commanded.** GE decides when to invoke Penny (the `docs/GE_FRICTION_BRIEF.md` brief documents the pain of GE "acting as the orchestrator with no controls exposed to us" — Penny experiencing imposition from above is the very reason orchestration moved in-house).

**The promise-friendly substrate.** Two things in the current design are already Promise-Theoretic in spirit, and Phase 2 builds on them rather than replacing them:

- The **contract documents** (`agent_contracts/*.xml` + FizzBee, per `docs/contracts-not-prompts.md`) are declarations by each agent about *its own* behavior, model-checked offline (`scripts/verify_fizzbee_contracts.py`, `a2a/workflows/fizz_check.py`) and mirrored by code enforcement (`<enforcement>` sections; `services/contract.py`). A published, verified statement of one's own intended behavior is precisely a promise.
- The **tool result convention**: every tool returns `{"ok": False, ...}` structured refusals (`concur_login_required_response`, `demo_policy_required_response`, `_receipt_store_required_response`) rather than raising across the boundary. Tools already *decline to cooperate* when their conditions aren't met — voluntary cooperation in embryo.

### 1.5 The current interaction graph

```
                         (command: invoke agent)
  Gemini Enterprise ────────────────────────────► ExpenseAgentExecutor
        │                                          executor.py
        │ Bearer ya29.* + text + FileParts             │ writes ContextVar (imposed context)
        ▼                                              │ stores receipt bytes
  Google tokeninfo                                     ▼
                                             penny_orchestrator  ◄─── agent_orchestrator.xml
                                              "owns EVERY turn"
                                   ┌───────────────┼────────────────┐
                     route/suspend │               │ route/suspend  │ direct tool calls
                            resume ▼               ▼                ▼
              penny_create_expense_report   penny_add_expense   orchestrator tools
                        │                        │  │            (list_open_reports,
                        │ create_report_         │  │ extract_    set_active_traveler…)
                        │ with_contract          │  │ receipt         │
                        ▼                        ▼  ▼                 ▼
                 services/contract.py   services/receipts.py   services/travelers.py
                        │               receipt_extraction.py  services/delegates.py
                        ▼                        │   │                │
                  SAP Concur ◄───────────────────┘   ▼                ▼
               (AsyncConcurClient)             Gemini vision     SAP Concur

  Shared mutable state (read/written across ALL of the above):
    EaMcpRuntime / Firestore users collection: refresh_token, active_traveler_login,
                                               active_report_{id,name,url}
    GCS bucket: receipts/{sub}/{sha256}
    Firestore adk_sessions: conversation state
```

Edges are commands (GE→executor, orchestrator→subagents), hidden shared-state dependencies (orchestrator ⇢ subagents via `active_traveler_login`), and synchronous calls. No edge is declared by its *target*.

---

## Phase 2 — Penny as a System of Promising Agents

### 2.0 Ground rules from the reference material

From Bergstra & Burgess, the tenets this redesign applies (ch. 1.3–1.4, ch. 2):

- **Autonomy**: "Agents are autonomous. They can only make promises about their own behaviour. No other agent can impose a promise upon them."
- **Promise**: a publicly declared intention, to an audience (its **scope**); made by a **promiser** to a **promisee** with a **body** *b* describing what it is about.
- **Polarity**: `A ──+b──► B` ("I will give/offer b") and `A ──−b──► B` ("I will accept/use b"). Cooperation *binds* only when a `+b` meets a matching `−b`; neither alone compels anything (§3.11).
- **Imposition**: "an attempt to induce cooperation in another agent … without prior invitation of promise to accept" — hints, requests, commands. An **obligation** adds a penalty for non-compliance.
- **Conditional promise**: `b|c` — "b given that c" (§3.4). A conditional promise combined with a promise to *acquire* the condition from a third party is an **assisted promise**: `A1 ──S|b(π)──► A2` together with `A1 ──−b(π)──► A2` ≡ `A1 ──S(b)──► A2` (Def. 31, eq. 6.26, and Law 4 "Assisted quenching of a pre-requisite promise").
- **Assessment**: "a decision about whether a promise has been kept or not. Every agent makes its own assessment about promises it is aware of." Promises are statements of intent; keeping them is never guaranteed — they "increase or decrease our certainty of a promised outcome" (§2.13).
- **Superagents**: agents compose; a cluster that makes collective promises externally (e.g. the server-pool superagent of fig. 4.4, whose members promise `+S` outward and coordination promises `C(...)` inward) is itself an agent. "We may choose the boundary of an agent wherever we please."

The design stance: **Penny's agents are already halfway there.** The FizzBee contracts are self-promises. What must change is (a) the orchestrator's claimed *ownership* of subagents, (b) the undeclared shared-state obligations, and (c) the absence of explicit `−` (acceptance) promises and assessments. Nothing below requires abandoning ADK; it requires re-*stating* the architecture so that every dependency is a voluntary, declared, assessable promise — and then letting the code follow the statements.

### 2.1 The agents, restated as autonomous promisers

Each box in the Phase 1 graph becomes an autonomous agent that publishes a **promise manifest**: what it offers (`+`), what it agrees to use (`−`), and under which conditions (`|c`). Notation: `π: Agent ──±body──► Promisee`.

#### A. `penny_create_expense_report` (CR)

The subagent stops being "invoked by the orchestrator" and instead *offers a service to anyone in scope* (scope = the Penny superagent's interior):

| Pol. | Promise body | Promisee |
|------|-------------|----------|
| + | `create_draft_report(name, purpose, date) ⟶ {reportId, webUrl}` \| `purpose_confirmed ∧ owner_resolved ∧ concur_connected` | Orchestrator (and transitively User) |
| + | `report.comment = PENNY_BOILERPLATE ∧ report.event = DEFAULT_EVENT` (unconditional — the invariants `CommentIsBoilerplate`, `EventIsDefault`) | User, Orchestrator, MLB compliance |
| + | `¬submit` — "I will never submit a report" (from its `description` and contract) | User, MLB |
| − | `use(active_traveler)` from the Session Registry | Session Registry |
| − | `use(concur_session)` from the OAuth Coordinator | OAuth Coordinator |
| − | `use(create_report API)` from Concur | Concur |

The conditions in the first promise are exactly the FizzBee guards on `CreateExpenseReport` (`require business_purpose_confirmed`, `require scenario == "standard" or owner_resolved`) — the contract already *is* the conditional promise body; today it is just never published to the promisees.

#### B. `penny_add_expense` (AE)

| Pol. | Promise body | Promisee |
|------|-------------|----------|
| + | `add_expense_line(report, type, date, amount, …) ⟶ {entryId}` \| `report_resolved ∧ type ∈ TWELVE ∧ purpose_confirmed ∧ (¬has_receipt ∨ receipt_readable)` | Orchestrator/User |
| + | `attach_receipt` \| `receipt_readable` — the `CreateRequiresReadableReceipt` assertion | User |
| + | `auto_itemize(hotel)` \| `all_lines_mapped ∧ reconciles`; **else** `+warn` (the `ItemizeHotel`/`WarnItemization` pair — a promise with an explicit fallback promise) | User |
| + | `refuse(type ∉ TWELVE) with supported list` (`expense_types.py` `classify_expense` statuses `unsupported`/`type_not_in_policy`) | User |
| − | `use(receipt_draft)` from OCR agent | OCR agent |
| − | `use(staged_receipt_bytes)` from Receipt Store | Receipt Store |
| − | `use(active_report)` from Session Registry | Session Registry |

#### C. `penny_orchestrator` (OR) — the big rewrite

Under the autonomy tenet, the orchestrator **cannot** promise that a subagent will create a report; it can only promise its own behavior. Its manifest shrinks to what it actually controls, and the "ownership" language is deleted:

| Pol. | Promise body | Promisee |
|------|-------------|----------|
| + | `classify_intent(message) into {create_report, add_expense, list, select, traveler, banter, oos}` | User, CR, AE |
| + | `relay(request → best-matching offered promise)` \| `an agent has published a matching +promise` | User |
| + | `resolve_traveler via approved roster before relaying delegate work` (the `ResolveTraveler` binding: `resolve_delegator` → `set_active_traveler`, never guessing) | User, CR, AE, MLB |
| + | `suspend/resume at most one workflow, only with user confirmation` (`RuleOfOne`, `PivotRequiresActiveWorkflow`) | User |
| + | `relay subagent results verbatim` (`CompleteWorkflow` guidance) | User, CR, AE |
| + | `report_listing ⟶ markdownTable verbatim` (`ListReports` render rule) | User |
| − | `use(create_draft_report)` offered by CR | CR |
| − | `use(add_expense_line)` offered by AE | AE |
| − | `use(session_context, delegator_roster)` | Session Registry, Concur |

The user-facing promise "Penny will create your expense report" is then an **assisted promise** (Def. 31): OR promises `report_created(b)` to the User, which decomposes as `OR ──report|b(CR's +create)──► User` plus `OR ──−b(CR's +create)──► User`. The user assesses Penny through the orchestrator as proxy — "it can only judge through the proxy of A1" — which matches the reality that GE users never see subagents.

Routing stops being command and becomes **selection among offers**: OR keeps a catalog of published `+` promises (today's `LlmAgent.description` strings are exactly this catalog, consumed by ADK's transfer mechanism) and promises only to *relay* the user's request to the matching offer. Whether CR accepts is CR's decision — and CR's contract already encodes its right to refuse (its tools return `{"ok": false}` refusals; its FizzBee guards block creation until *it* has confirmed the purpose with the user).

#### D. `ExpenseAgentExecutor` (EX) — the gateway agent

| Pol. | Promise body | Promisee |
|------|-------------|----------|
| + | `verified_identity(sub, email)` \| `valid bearer token` — else the unauthenticated refusal (`executor.py` "I couldn't verify your identity…") | OR, CR, AE, Receipt Store |
| + | `stage(receipt bytes → GCS(sub, sha256)) ⟶ StagedReceiptRef` | AE, Receipt Store |
| + | `progress frames while tools run` \| `client opened message/stream` (the `_rpc_method` check) | GE/User |
| + | `deliver final reply + A2UI upgrade, degrading gracefully to text` (`_compose_reply_parts`; a2ui.py docstrings promise "graceful degradation") | GE/User |
| − | `use(A2A messages with Bearer + FileParts)` from GE | GE |
| − | `use(orchestrator's final response)` | OR |

#### E. Receipt OCR agent (OCR)

| Pol. | Promise body | Promisee |
|------|-------------|----------|
| + | `draft{vendor, date, amount, categoryGuess, lineItems} + readable flag` \| `Date ∧ Vendor ∧ Amount legible` — else `readable=false` + resubmission guidance (`REQUIRED_RECEIPT_FIELDS`, `validate_receipt_draft`) | AE |
| + | `non-authoritative: every draft requires user confirmation` (module docstring: "nothing here is authoritative") | AE, User |

This is a textbook honest promiser: it declares the limits of its own reliability in the promise body, and AE's `−` promise (use the draft) is explicitly conditioned on user confirmation downstream.

#### F. Session Registry (SR) — promoting shared state to an agent

The most important structural change. Today `EaMcpRuntime`/Firestore is a blackboard that OR writes and subagents silently read — the hidden imposition of §1.4. Promise Theory says: draw the agent boundary around it ("we may choose the boundary of an agent wherever we please") and make its behavior explicit:

| Pol. | Promise body | Promisee |
|------|-------------|----------|
| + | `current active_traveler is X, set at time t by OR on behalf of user u` — provenance included | OR, CR, AE |
| + | `current active_report is (id, name, url)` \| `one was resolved` | OR, AE |
| + | `persist refresh_token keyed by Google sub; never leak across subs` (`EaSessionStore`, `receipt_user_scope`) | User, OAuth Coordinator |
| − | `accept traveler/report updates only from an agent presenting verified_identity(sub)` | OR, EX |

Once SR publishes `+active_traveler` and CR/AE publish matching `−use(active_traveler)` promises, the dependency that was invisible becomes a **binding** in the promise graph — assessable, testable, and impossible to forget when adding workflow #3.

#### G. External agents: Concur, GE, and the User

- **Concur** cannot be commanded. Penny holds `−use` promises against Concur's published `+API` promises (the OpenAPI specs in `concur_openapi/` *are* Concur's promise documents). Penny's `ConcurResponse[T]` (`concur_client/_responses.py`, README §Responses) is the **assessment apparatus**: `raise_for_status()` / `parse()` are Penny deciding, locally and autonomously, whether Concur kept its promise. The `idempotency_id` on `create_new_report` is Penny engineering for the tenet that *keeping is never guaranteed* — safe retry when the assessment is "unknown."
- **GE** imposes invocations. Penny cannot prevent that, but it shapes the imposition into near-cooperation by publishing its **agent card** (`agent/agent_card.py`, `/.well-known/agent-card.json`) and **invocation specification** (`agent/invocation_spec.py`, `AGENT_INVOCATION_DESCRIPTION`): these are literally `+` promises in GE's scope — "invoke me for Concur expense tasks…; I do not submit reports." An imposition that lands on a matching published promise reduces to cooperation (eq. 3.40: imposition + promise to accept ≃ binding).
- **The User** is an autonomous agent too. Penny's confirmation gates (`ConfirmBusinessPurpose` in both subagent contracts; A2UI Confirm/Edit buttons in `a2ui.py`) are Penny *soliciting a promise* from the user (`+purpose_confirmed`) rather than assuming one — the user's reply is the `−`/`+` that completes the binding before anything is written to Concur.

### 2.2 Where the current design imposes, and the voluntary-cooperation rewrite

| # | Current imposition (code) | Rewrite as voluntary cooperation |
|---|---------------------------|----------------------------------|
| 1 | **"The orchestrator owns EVERY turn"** and routes/suspends/resumes subagents (`agent_orchestrator.xml` objective; `RouteToWorkflow`, `ConfirmPivot`, `ResumeWorkflow`) | OR promises only its own behavior: classify, relay, remember one suspension. CR/AE publish `+workflow` offers with conditions; OR holds `−use` promises against them. "Suspend" becomes OR's promise to *stop relaying* to CR and to remember the context — CR needs no cooperation to be suspended, because suspension was never something done *to* it, only a change in what OR relays. |
| 2 | **Orchestrator writes `active_traveler_login`; subagents silently read it** (`ResolveTraveler` comment; `_resolve_active_traveler_email` in `agent/context.py`) | SR agent publishes `+active_traveler` with provenance; CR/AE declare `−use(active_traveler)` and make their workflow promises conditional on it: `create_report | active_traveler_published`. The subagent's refusal path (today's `active_traveler_email_required_response()` with hint "Call set_active_traveler … then retry") already exists — it becomes the declared behavior when the condition promise is absent, not an error. |
| 3 | **Executor imposes per-request context via `ContextVar`** (`set_request_context`) — tools cannot function without an ambient value they never asked for | EX publishes `+verified_identity` and `+staged_receipts` per turn; tools declare `−use` promises. Mechanically the ContextVar can stay, but `require_agent_invocation()` is re-documented (and eventually re-typed) as *acceptance of EX's offer*, with its `auth_required_response()` as the declared no-binding outcome. |
| 4 | **`create_report_with_contract` silently overwrites comment/event** — server discards anything the LLM passes (`services/contract.py`) | Keep the behavior, fix the statement: CR *promises* `comment = PENNY_BOILERPLATE` unconditionally to the compliance scope. What is imposition against the LLM today becomes CR's own published invariant — defense in depth restated as a promise the code keeps on the agent's behalf. |
| 5 | **GE commands Penny with no negotiation** (`GE_FRICTION_BRIEF.md`) | Cannot be fixed unilaterally — autonomy cuts both ways. Penny's lever is the fidelity of its published promises (agent card, invocation spec) so GE's impositions land on declared `+` promises, and structured refusals when they don't (the `out-of-scope` response template is exactly a declined imposition). |
| 6 | **Hard construction-time coupling** (`build_orchestrator_agent()` imports both subagent builders) | Registration by manifest: subagents register their `+offers` (id, conditions, tools) and OR consumes the registry — the `iter_contract_docs()` machinery in `contract_doc.py` already discovers every `agent_*.xml`; extend it to carry the promise manifest (see refactoring R2). |

### 2.3 Conditional promises where the code has dependencies

Every FizzBee `require` maps onto a conditional promise body; the dependency chain becomes a chain of conditions each agent quenches via a `−` promise to a third party (Law 4):

```
CR ──  +create_report | purpose_confirmed ∧ owner_resolved ∧ concur_connected  ──► OR/User
CR ──  −purpose_confirmed        ──► User            (ConfirmBusinessPurpose gate)
CR ──  −owner_resolved           ──► SR              (active_traveler from registry)
CR ──  −concur_connected         ──► OAuth Coordinator

SR ──  +active_traveler | roster_verified            ──► CR, AE
OR ──  +roster_verified          ──► SR              (resolve_delegator matched, never guessed)
OR ──  −delegator_roster         ──► Concur          (list_delegators / delegates.py)

AE ──  +expense_line | report_resolved ∧ type∈TWELVE ∧ purpose_confirmed
                     ∧ (¬has_receipt ∨ receipt_readable)                    ──► OR/User
AE ──  −receipt_readable         ──► OCR             (extract_receipt.readable)
AE ──  −staged_receipt           ──► EX/ReceiptStore (sha256 reference)
AE ──  +auto_itemize | all_lines_mapped ∧ reconciles ──► User
AE ──  +itemize_warning | ¬(all_lines_mapped ∧ reconciles)                  ──► User
```

Because CR promises both `create|owner_resolved` *and* `−owner_resolved` (it will acquire the owner from SR), the pair reduces to the assisted promise `CR ──create(owner)──► User` — which is exactly what the user experiences, while the graph preserves who actually quenches each prerequisite. Note what the theory adds over the FizzBee guards: the guards say *when CR may act*; the conditional promises say *who CR relies on for each condition and that the reliance is agreed*, which the guards alone never expressed.

### 2.4 The promise graph vs. the current interaction graph

```
                 PENNY SUPERAGENT boundary ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┐
   GE ──imposes──► EX                                                    ┆
   GE ◄──+agent-card, +invocation-spec (Penny's collective promise)      ┆
        ┆                                                                ┆
        ┆   EX  ──+identity, +staged_receipts──────►  (all interior)     ┆
        ┆   EX  ──−final_reply──► OR    OR ──+reply──► EX                ┆
        ┆                                                                ┆
        ┆   OR  ──−create_report──► CR   CR ──+create_report|c₁──► OR    ┆
        ┆   OR  ──−add_expense──►  AE   AE ──+expense_line|c₂──►  OR     ┆
        ┆                                                                ┆
        ┆   CR,AE ──−active_traveler──► SR   SR ──+active_traveler──► *  ┆
        ┆   AE  ──−draft──► OCR   OCR ──+draft|readable──► AE            ┆
        ┆   AE,EX ──−bytes/+bytes──► ReceiptStore                        ┆
        └┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┘
   Penny ──−API──► Concur      Concur ──+API (OpenAPI specs)──► Penny
   Penny ──−purpose_confirmed──► User  User ──+confirmation──► Penny
```

Differences from the Phase 1 graph, and why they matter:

1. **Every edge is bidirectional and typed.** The current graph has anonymous arrows (calls, writes). The promise graph pairs every `−` with a `+`; an unmatched `−` (an agent consuming something nobody promised) is a *detectable design defect*. Today's codebase has exactly one big unmatched `−`: subagents' use of `active_traveler_login`, promised by no one.
2. **No ownership edges.** OR→CR "route/suspend/resume" command edges disappear; what remains is OR's `−use` of CR's conditional offer. The subagents' guards were always the real gate — the graph now says so.
3. **The graph is declarative and static-checkable.** Like the FizzBee contracts, the promise manifests can be verified offline: binding completeness (+/− matching), condition quenching (every `|c` has some agent promising `+c`), scope validity. This extends the `contracts-not-prompts` wager from single-agent state machines to the *inter-agent topology*.
4. **Failure semantics are local.** In the command graph, a subagent failure is the orchestrator's problem to interpret. In the promise graph, CR failing to keep `+create_report` is assessed independently by OR (which promised only to relay outcomes) and by the User. Nobody's promise *obliges* anyone else to compensate — compensation, if wanted, must itself be promised (e.g., OR's `+relay_error_verbatim`, which the CR contract's `<responses>` error templates already implement).

### 2.5 Assessment and trust

Promises are about intent; keeping them is never guaranteed. Each agent assesses autonomously:

**Assessment mechanisms Penny already has** (and should recognize as such):

- `ConcurResponse.raise_for_status()/.parse()` — Penny's per-call assessment of Concur's API promise. A parse failure is an assessment of "promise not kept (malformed body)," distinct from a 4xx "promise not kept (refused)."
- `runtime.py` `_log_granted_scopes()` — comparing requested vs granted OAuth scopes is a *documented* assessment of Concur's authorization promise: "Concur only ISSUES scopes the app registration is approved for … it silently drops the rest." That log line is the canonical example of promise-vs-outcome divergence in this codebase.
- `validate_receipt_draft` / the `readable` flag — AE's assessment of the OCR agent's draft promise before relying on it.
- `verify_fizzbee_contracts.py` + the `verified="fizz-0.5.1"` attribute stamped in each contract — *pre-assessment*: proof that an agent's promise set is internally consistent before it is ever made. The pytest `<enforcement>` mirrors are repeated offline assessments.
- The itemization `reconciles` check (`services/itemization.py`, `ItemizeRequiresMappedAndReconciled`) — AE assessing *its own* ability to keep `+auto_itemize` before promising it, and downgrading to `+warn` when it can't.

**What's missing: an assessment ledger, and trust as its integral.** Trust, in the reference material, is the accumulated valuation of an agent's promise-keeping that modulates how much another agent relies on it ("no matter how trustworthy a promise might be, it can increase or decrease our certainty of a promised outcome"). Penny assesses constantly but records nothing, so every turn starts from zero trust. Concretely:

- EX/OR should record, per (agent, promise-type): promised, kept, not-kept, unknown — e.g. a Firestore `assessments` collection next to `adk_sessions`. The `_TOOL_PROGRESS` hook in `executor.py` already intercepts every tool call; it is the natural tap point.
- Trust then *modulates reliance, never obligation*: low OCR trust for a vendor class → AE tightens its confirmation prompt (asks the user to verify amount explicitly); repeated Concur 401s on a scope → OR proactively promises the reconnect flow (`disconnect_concur` guidance) instead of retrying; high CR keep-rate → OR relays with less hedging in progress text.
- The User's trust is managed the same way: `PENNY_REPORT_COMMENT` ("Penny is still in training, and the User is required to verify all values before submitting") is Penny publicly calibrating the user's expected assessment — an honest low-trust self-declaration. As the assessment ledger matures, that boilerplate can cite evidence rather than blanket caution.

Crucially, assessments are subjective and local: GE may assess a Penny turn as failed (timeout) while Penny assesses it as kept (report exists in Concur) — the friction brief documents precisely this divergence. The promise graph doesn't eliminate the divergence; it names whose assessment is whose, which is what makes the GE conversation in `GE_FRICTION_BRIEF.md` tractable ("your orchestrator broke *its* promise; ours kept *ours*").

### 2.6 Superagents: composition and emergence

**Penny itself is the worked example.** From GE's vantage point there is exactly one agent — the agent card at `/.well-known/agent-card.json` promising "Manage Concur expenses," no submit, receipt OCR. Inside the boundary, that collective promise is *emergent from* the sub-promises: EX's identity/staging promises, OR's classification/relay promises, CR's and AE's conditional workflow promises, SR's state promises, OCR's draft promises. This is the book's server-pool pattern (fig. 4.4): members promise `+S` outward through a common face, plus interior coordination promises `C(...)` invisible to the client. The agent card is the superagent's promise; `agent_card.py` is where it is authored; the sub-promise manifests are what must *entail* it. A useful discipline follows: **no capability appears on the agent card unless the interior promise graph can derive it** — e.g. the card's "attaches receipts only when the photo is readable" is derivable from AE's `+attach|readable` and OCR's `+readable` assessment. That derivation is reviewable in a way "the prompt says so" never was.

**Interior superagents.** The (CR + `services/contract.py`) pair is itself a two-member superagent: the LLM half promises to *follow* the contract, the code half promises to *enforce* it; their conjunction is what makes `CommentIsBoilerplate` a promise Penny can keep against a stochastic executor. The same holds for (AE + `expense_types.py`) on the twelve-type whitelist. `docs/contracts-not-prompts.md` calls this defense in depth; in promise terms it is a coordinated promise made jointly by two agents with very different keeping-probabilities.

**The legacy architecture was a superagent too** — Receipt Intake A2A + EA MCP cooperating through GCS with the Google `sub` as shared key (`RECEIPT_INTAKE_A2A.md`: "Two GE integrations cooperate… The Google `sub` is the shared key"). Its promises were kept via a *stigmergic* channel (shared store) with no coordinator at all — evidence in Penny's own history that promise-based cooperation without central control works. The unified agent collapsed that boundary for GE-friction reasons, not because the cooperation failed.

### 2.7 Prioritized refactorings for the Penny codebase

Ordered by (architectural leverage) / (implementation risk):

**R1 — Make the traveler/report dependency an explicit promise binding.** *(highest value, small diff)*
Add `active_traveler` / `active_report` as declared inputs in the subagent contracts (`agent_create_expense_report.xml`, `agent_add_expense.xml`): a new `<uses>` (i.e. `−` promise) section naming SR as the counterparty, and the condition already present in the FizzBee guards. In code: pass the resolved traveler explicitly in the handoff context at `RouteToWorkflow` (the orchestrator guidance already says to pass reportId/reportName — extend to traveler) so subagent tools stop re-deriving it ambiently via `_resolve_active_traveler_email()`. Files: `agent_contracts/*.xml`, `a2a/workflows/orchestrator.py`, `agent/context.py`.

**R2 — Promise manifests in the contract documents, with offline binding verification.** Extend the `ContractDoc` schema (`a2a/workflows/contract_doc.py`) with a `<promises>` block: `<offer body="…" condition="…" promisee="…"/>` and `<use body="…" from="…"/>`. Add `scripts/verify_promise_graph.py` beside `verify_fizzbee_contracts.py` that loads all manifests via `iter_contract_docs()` and checks: every `−` has a matching `+`; every condition `|c` is quenched by some agent's `+c`; the agent card's advertised skills are entailed by interior offers. Mirror with a pytest (pattern: `tests/a2a/workflows/test_fizzbee_contract.py`).

**R3 — Rewrite the orchestrator contract from ownership to relay.** Edit `agent_orchestrator.xml`: replace "The orchestrator owns EVERY turn" with a manifest of OR's own promises (classify, relay, one-suspension memory, verbatim relay of results); recast `RouteToWorkflow` guidance as selection among subagent *offers* (sourced from their manifests, not hard-coded); keep the FizzBee machine — its guards are OR's own conditional promises and survive unchanged. Then decouple construction: `build_orchestrator_agent()` builds `sub_agents` from the manifest registry instead of direct imports.

**R4 — Assessment ledger + trust surface.** New module `expense_core/services/assessments.py`: record `(agent, promise_body, outcome ∈ {kept, not_kept, unknown}, t)` for (a) every Concur call outcome (tap `ConcurResponse`), (b) OCR readability outcomes, (c) subagent workflow completions. Persist beside `adk_sessions` in Firestore (`EaSessionStore.database`). First consumers: `_log_granted_scopes`-style structured logging, and an AE prompt tweak that strengthens user confirmation when OCR keep-rate for the receipt's category is low.

**R5 — Structured refusals as first-class promise outcomes.** Unify the ad-hoc refusal dicts (`concur_login_required_response`, `demo_policy_required_response`, `_receipt_store_required_response`, `auth_required_response`) into one shape carrying *which promise could not bind and which condition failed* (e.g. `{"ok": false, "promise": "create_report", "unmet": "concur_connected", "remedy": authorizeUrl}`). Tools already return these; standardizing lets OR relay unmet-condition information mechanically and lets R4 log them as `not_kept(condition)` rather than generic errors. Files: `expense_core/oauth.py`, `expense_core/session_tools.py`, `agent/context.py`, `agent/tools.py`.

**R6 — Stop silently downgrading the session-persistence promise.** `server.py` falls back to `InMemorySessionService` with only a log warning when Firestore is unavailable — Penny then *breaks* its implied promise of cross-restart session memory (`docs/AGENT.md` §Session memory) without telling anyone in scope. Either refuse to start (don't make the promise) or degrade the published promise: surface "session memory unavailable" in `get_session_context` so OR can inform the user. Small change, high honesty value.

**R7 — Emit the agent card from the promise graph.** Once R2 exists, generate the skills/description sections of `agent_card.py` and `invocation_spec.py` from the union of interior `+` promises (with the no-submit negative promises included), so the superagent's external promise can never drift from what the members actually offer. This is the same single-source-of-truth move `contract_doc.py` already made for instructions-vs-model-checking, applied one level up.

**R8 — (Exploratory) Per-workflow keep-rate in the user-facing boilerplate.** Replace the static `PENNY_REPORT_COMMENT` caution with evidence-linked calibration from R4's ledger. Low priority; touches compliance language.

---

## Closing note

The deepest finding of this analysis is that Penny's *intra-agent* discipline is already Promise Theory in disguise: each contract document is a model-checked declaration about the agent's own behavior, enforced in code, with structured refusal as the non-cooperation path. What the codebase lacks is the *inter-agent* half of the theory — declared acceptances (`−` promises), explicit conditions naming their quenchers, an assessment record, and a superagent promise derived from (rather than asserted alongside) its members. None of the eight refactorings above requires abandoning ADK, A2A, or the FizzBee contracts; they extend the "contracts, not prompts" wager (`docs/contracts-not-prompts.md`) from *"can this agent reach a bad state?"* to *"can this system of agents make a promise it has no way to keep?"* — and make that question mechanically checkable before deployment.
