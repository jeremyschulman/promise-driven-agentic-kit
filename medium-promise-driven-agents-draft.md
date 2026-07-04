# You Can't Command an LLM. So Stop Trying.

### How a 20-year-old theory finally gave me a way to build agents I can trust — and how you can build them too

*By Jeremy Schulman*

---

I've spent most of my career getting unruly systems to behave. Networks, mostly — multi-vendor, multi-domain, the kind where a single wrong change at the wrong moment ruins somebody's night. So when I started building LLM agents, I thought I knew the drill. Write down the rules, be precise, cover the edge cases, ship it.

It did not go well.

I want to tell you about the wall I hit, the 20-year-old theory that finally explained *why* I kept hitting it, and — this is the part I'm actually excited about — a concrete, runnable way I found to build agents on top of that theory. Not theory for its own sake. A method you can pick up and use on Monday. I think it's one of the more important shifts in how we build agentic software, and I want to make the case to you as plainly as I can.

Let me start with the wall.

## Part 1 — The wall: a prompt is not a command

Here's the kind of instruction I was writing, and I'd bet you've written one just like it:

> *"You are a helpful clinic assistant. Always verify the patient's identity before booking anything. Never book an appointment that isn't covered without confirming self-pay first. Never double-book a time slot."*

It reads beautifully. It sails through a design review. Everyone nods. And it is **impossible to verify**.

I learned this the way everyone learns it: in the logs. The agent booked an appointment before it had verified who it was talking to. It offered a slot, the slot got taken, and it cheerfully booked a *different* time nobody asked for. Each time, I did the thing we all do — I went back to the prompt and added another sentence. "Really, seriously, always verify first." "Do NOT book a different slot." I was negotiating with it.

And one day it hit me that I was making a category mistake. I was writing those instructions as if I were programming a computer — as if the words were *commands* the model would *execute*. But that's not what an LLM is. An LLM is a stochastic sampler. On any given turn it might classify intent wrong, skip a step, or invent a tool argument. No wording fixes that, because the problem isn't the wording. The prompt was never a command. It was a **request** — a hopeful one.

For a one-shot Q&A bot, who cares. A wrong turn is cheap and the next question resets everything. But for a **stateful, multi-step, safety-sensitive** agent — one that touches money, identity, or anything you can't undo — that category mistake is the origin of every incident that keeps you up at night. Because it leaves the one question you actually need answered completely unanswerable:

> *Can this agent ever reach a state it must never be in?*

With a prose prompt, the most honest answer I could give was: *"Probably not. But I can't prove it."*

I hate that answer. It's the "oh crap, is it the network?" of agent design — that sinking feeling when something's wrong and you have no way to know if your system is the cause. I've spent years trying to get operators from "oh crap" to "all clear" with confidence. A prompt gives you no path there. So I went looking for one.

## Part 2 — The reframe: an LLM is an autonomous agent

The thing that unstuck me wasn't an AI paper. It was a body of work from configuration management and distributed systems called **Promise Theory**, developed by Mark Burgess (and formalized with Jan Bergstra). It's been around for about two decades. I'd bumped into it years ago in the network automation world and filed it away as interesting. Rereading it with agents on my mind, I sat up straight.

Promise Theory reasons about systems built from **autonomous** parts. Its founding axiom is deceptively simple:

> An agent is autonomous. It can only make promises about *its own* behavior. No other agent can impose a promise upon it.

You cannot force another agent to do anything. You can only *ask* — and it decides. In Promise Theory, that ask has a name: an **imposition**. A command, a hint, a request — all impositions, and all of them guarantee exactly nothing, because the target is autonomous. The only thing an agent can actually offer you is a **promise**: a declaration *about itself* that you, the recipient, can then rely on and — this is the key word — **assess**.

Now read that axiom again with an LLM in mind. Here's the part that made me sit up:

**Everything Promise Theory says about autonomous agents is true of an LLM as a matter of engineering fact — not as a metaphor.**

- You cannot impose behavior on it. No prompt *guarantees* an action.
- The most a prompt can do is *elicit a promise* to behave a certain way. Because the promiser is stochastic, you the recipient **must** verify.
- It's just one autonomous agent among several — the model, the code around it, the external APIs, the human. No privileged commander in the room.

That's the whole reframe, and it changed how I build. Teams that treat prompts as commands spend their lives asking "why won't it obey?" Teams that treat prompts as **promises requiring assessment** build the verification layer on day one. I'd been living in the first camp. I wanted to move to the second.

If you take one idea from this article, take this one: **you can't command an LLM. You can only elicit a promise and then assess whether it was kept.** I've started calling the whole approach that follows from it **promise-and-assess**. Everything else in this piece is me trying to make that phrase concrete enough to build on.

## Part 3 — The gap nobody talks about

Here's where most write-ups about Promise Theory and AI stop. They land the beautiful reframe, quote the axioms, and leave you nodding — and with absolutely no idea what to do Monday morning.

That gap bugged me for weeks. Promise Theory is, frankly, PhD-level material. It has formal definitions, polarities, a whole algebra of conditional promises. The reframe is genuinely clarifying. But "treat your LLM as an autonomous promiser" is not something I can hand to an engineer and say "go build it." Where does the promise *live*? What file is it in? How do I check it? How does it survive contact with a real framework and a real deploy?

That's the question this whole piece is really about: **how do you get from a profound idea to something you can actually run?**

I ended up building it out, end to end, as an open-source kit with two complete, runnable example agents. Let me show you the bridge I found. There are only a handful of moving parts, and none of them are exotic.

## Part 4 — The bridge: one artifact, three readers

Here's the move that made everything click. Instead of a prose prompt, each agent's *entire* instruction set becomes a single document — I call it a **contract**. And the trick is that this one document is read by three different consumers, each taking what it needs:

1. a **model checker**, which proves the agent can never reach a bad state,
2. the **code that builds the agent**, which reads the agent's declared promises, and
3. the **LLM itself**, which reads the whole thing as its operating instructions.

One artifact. Three readers. Same bytes. That last part matters more than it sounds, and I'll come back to it.

At the center of the contract is a small **state machine**, written in a language called [FizzBee](https://fizzbee.io) — it's in the TLA+ family of formal specification languages, but with a Python-ish syntax that reads approachably. Here's the actual rule from the clinic assistant I mentioned, verbatim:

```python
atomic action VerifyPatient:
    require not patient_verified
    require active_workflow == NO_WORKFLOW
    patient_verified = oneof [True, False]

always assertion PatientVerifiedBeforeWorkflow:
    return active_workflow == NO_WORKFLOW or patient_verified
```

You don't need to know FizzBee to read that. In plain English:

- An **action** is something the agent can do. The **require** lines are *guards* — preconditions. `VerifyPatient` can only run when the patient isn't yet verified and no workflow is active.
- `oneof [True, False]` says the outcome is uncertain — verification might succeed or fail.
- An **always assertion** is an *invariant* — something that must be true in **every** reachable state. `PatientVerifiedBeforeWorkflow` says: either no workflow is running, or the patient is verified. There is no legal state where a workflow runs on an unverified patient. Full stop.

Now here's the payoff. A **model checker** takes that machine and explores *every reachable combination of states* the actions can produce, and confirms no invariant is ever broken. I run it offline, in CI, before anything ships:

```
[PASS] book_appointment
[PASS] clinic_orchestrator
[PASS] manage_appointment
3/3 contract(s) passed model checking.
```

Remember my unanswerable question — *"can it ever reach a bad state?"* This answers it. Not with "probably not." With **"no, and here's the exhaustive proof."**

And I want to be clear this is not a toy that only passes because I wrote it to pass. My second example is the Trials of the Holy Grail — yes, the Monty Python one, knights and the Bridge of Death and the Knights Who Say "Ni!" — and it has a Quest Marshal that's supposed to grant the Grail quest only after *both* trials are passed. **Its first draft failed model-checking.** The checker found a sequence I never would have: a knight could re-attempt a trial he'd already passed, fail it *after* the Grail was granted, and blow the invariant. The tool handed me the exact step-by-step trace to the bad state. The fix — make a passed trial "sticky" — took two minutes. That's a real bug, caught by exhaustive search, before any human or any model ever saw the agent. Prose could never have caught that.

Let me say the thing about "same bytes" now, because it's the quiet hero here. In the usual setup — say, a state machine coded in one place and a prompt written in another — the machine and the instructions are *two different artifacts that drift*. You fix one, forget the other, and find out in production. Here, the state machine the checker proves and the instructions the model reads are **the same document**. They can't drift, because there's nothing to drift from.

## Part 5 — Formalize the structure, leave judgment to prose

Now, I am *not* telling you to formalize your whole agent. That way lies madness. The single most useful rule I found is about where to draw the line:

> **Formalize structure and ordering. Leave judgment and phrasing to prose.**

"Verify before you book," "never double-book," "at most one task can be suspended" — those are structural. They're about ordering and safety, and they belong in the model-checked state machine, because prose lets them drift.

But "is this message a greeting or a booking request?" is not a formal property and never will be. Neither is "how do I phrase this hand-off warmly?" That's judgment. It stays in prose — in a section of the contract I call step-guidance — right alongside the formal parts, but clearly quarantined from them.

Don't try to formalize the fuzzy stuff; you'll fail and hate your life. Don't leave the structural stuff to prose; it'll drift and hurt you. Getting that division right is most of the skill.

## Part 6 — The part you cannot skip

I need to be honest with you about the biggest caveat, because it's the thing that separates a real contract from theater.

**Model-checking proves the specification. It does not prove the LLM follows the specification.**

The proof certifies that the *state machine* can't reach a bad state. It says nothing about whether your stochastic model actually stays on the legal path. The model can still misread eligibility, skip a guard, or fabricate an argument. If you model-check your contract, ship it as a prompt, and stop there — you've bought yourself false confidence, which is worse than no confidence.

Promise Theory explains exactly why, in one line: *a promise from an unreliable promiser is worthless to you without independent assessment.*

So every safety invariant gets a twin. Take the no-double-book rule:

```python
always assertion NoDoubleBook:
    return (not appointment_booked) or slot_available
```

That invariant is the LLM's *promise*: "I'll never book a taken slot." The **assessment** is real code — the scheduling service itself refuses to commit a slot that isn't open, no matter what the model says. The model can promise all day; the code is what decides whether the promise was kept, and quietly refuses when it wasn't.

This LLM-promise-plus-code-assessment pair is, to me, the atomic unit of the entire method. **Never a stochastic promise standing alone. Always a stochastic promise backed by a deterministic assessment.** The model check proves the map is coherent; the code polices the territory. You need both, and the code half is not optional.

## Part 7 — From one agent to a system of agents

Everything so far makes a *single* agent trustworthy. But the clinic isn't one agent — it's a small society of them behind one friendly face: an orchestrator that verifies you and routes your request, a booking subagent, a subagent that cancels and reschedules, plus non-LLM service agents for the schedule, the insurance check, and the patient registry.

This is where I think Promise Theory earns its keep most, because multi-agent systems usually rot in the same place: **hidden dependencies.** One agent writes some shared state, another silently reads it, and nobody declared the handoff. It works until it doesn't.

Promise Theory drags every one of those dependencies into the open, using two polarities. An agent makes an **offer** (`+`) — "I provide this" — or a **use** (`−`) — "I rely on this." And here's the rule that does the work: cooperation only *binds* when a `+` offer meets a matching `−` use. An offer nobody uses, or a use nothing offers, is a **design defect you can detect mechanically.**

Each agent publishes a little manifest of its offers and uses. Here's the booking agent promising not to double-book, written as an offer:

```xml
<offer id="never_double_book" type="invariant" to="patient clinic-compliance">
  <body>A slot is never booked twice; the commit is refused by the provider
    schedule if the slot was taken since it was offered (NoDoubleBook, kept in
    code regardless of the model).</body>
</offer>
```

Notice the body names its own division of labor: the LLM promises it, but the guarantee is *kept* by the schedule service refusing a taken slot. That's the promise-and-assess pair again, made explicit for anyone reading the manifest.

Three consequences fall out of this, and they're the reason I now design this way:

**The orchestrator owns nothing.** This one took me a while to accept. Under the autonomy axiom, the orchestrator *cannot* promise that a subagent will book anything — it can only promise *its own* behavior: verify the patient, classify intent, relay to the subagent whose offer matches, remember at most one suspended task, relay the result. Routing stops being a *command* and becomes **selection among published offers**. The orchestrator doesn't reach inside a subagent and make it act. It uses the subagent's conditional offer, and the subagent's own guards are the real gate. If the subagent refuses, the orchestrator relays the refusal — it doesn't override it.

**Shared state becomes an agent.** Instead of a blackboard the orchestrator scribbles on and the subagents peek at, the patient registry is its own agent that *publishes* the verified patient. Consumers declare that they rely on it. The invisible dependency becomes a declared, checkable binding — impossible to forget when you add a third workflow six months later.

**The whole graph is verified offline.** Just like the state machines get model-checked, the promise manifests get checked for completeness: every `−` use meets a `+` offer, and every condition is either satisfied by some agent's offer or explicitly marked self-assessed. An agent relying on something nobody promised is a **build failure, not a 2 a.m. surprise.**

So the wager scales. For one agent it was *"can this reach a bad state?"* For the system it becomes *"can this society of agents make a promise it has no way to keep?"* — and I get to answer that before I deploy, too.

Oh, and one more thing that pleased me more than it should have. The two examples — the clinic and the Holy Grail — run on **different frameworks** (the clinic on Google's ADK, the Trials on Pydantic AI). They share the *same* contracts and the *same* enforcement code. The only meaningful difference between them is a single file that wires them to their runtime. Everything that makes them *safe* is identical and framework-independent. That told me the method lives in the contracts and the assessment code — not in anybody's framework-of-the-month.

## Part 8 — What you actually walk away with

I don't want to leave you with a vibe. Here's the distilled standard I now hold my own agents to. If you build nothing else from this article, run your current agent design past these:

1. **Treat every model as an autonomous agent.** Design for elicited promises and mandatory assessment, not for compliance. This ends the "why won't it obey?" spiral, because you stop expecting obedience.
2. **Make each agent's self-promises a model-checked contract.** Formalize ordering and safety as a state machine; prove it exhaustively offline. Keep judgment in prose, quarantined so it can't corrupt the guarantees.
3. **Every condition names who satisfies it.** No hidden dependencies. A condition is either self-assessed or met by a named agent's offer.
4. **Pair every stochastic promise with a deterministic assessment.** The enforcement code isn't belt-and-suspenders. It's the whole point. Never ship the contract without it.
5. **Declare what you rely on; forbid unmatched edges.** Every use meets an offer. Relying on something nobody promised is a build failure.
6. **Derive the outside promise from the inside.** What your system advertises to the world should be generated from what its members actually offer — so it can never overstate what it delivers.

Points 1–2 make a single agent trustworthy. That's where most teams stop, if they get there at all. Points 3–6 make a *system* trustworthy. I genuinely believe this is where agentic engineering is heading, whether or not anyone uses the word "promise" — because the premise underneath it is just *true*: the model is an autonomous stochastic agent, and autonomous agents can only be promised, then assessed.

## Part 9 — When *not* to do this

I'd be doing you a disservice if I pretended this is free. It isn't, and knowing where it *doesn't* pay off is part of using it well.

A formal contract is more work than a paragraph. It costs tokens every single turn, because it rides in the context window. It asks your team to read a state machine and run a model checker in CI. And — I'll say it a third time because it's the trap — the model check proves the spec, not the behavior, so the enforcement code is mandatory, which is *more* engineering, not less.

So **skip it** for one-shot Q&A, a single-tool lookup, or a throwaway prototype where a wrong turn costs nothing. There, a good prose prompt is exactly the right tool, and a contract is just ceremony.

**Reach for it** when you've got multi-step workflows, ordering or safety constraints that truly must hold, actions involving money or identity or anything irreversible, and a system you need to evolve without quietly regressing. That's precisely the situation where "probably not, but I can't prove it" isn't good enough — and it's the situation I keep finding myself in.

## Part 10 — Go build one

I opened with a wall: I couldn't answer whether my agent could reach a state it must never be in. Here's where I've landed. The clinic assistant takes "I'm Ada Lovelace, book me a dermatology visit" and turns it into a confirmed, eligibility-checked appointment — through identity verification, a coverage check, and a real scheduling API — and it *cannot* reach a state where it books before you're verified or double-books a slot. Not because I asked it nicely. Because the contract made those states provably unreachable, the code made every promise assessed, and the promise graph made every dependency something we declared out loud.

That's the shift I got excited enough about to build out and give away. It's not the last word — I'm sure smart people will improve on it, and I'd love that — but I think it's a real answer to a real question, and it's ready for you to pick up.

I packaged the whole thing as an open-source kit: the two runnable examples (clinic and Holy Grail), the schemas, a project template that scaffolds a new contract-driven agent that's green out of the box, and an authoring skill that walks you through writing your first contract. You can model-check the examples *and talk to them.*

So here's my ask: go build one. Take a small, stateful agent you already have — one where a wrong turn actually costs something — and try writing its rules as a contract instead of a prompt. Run the model checker. Watch it find the state you didn't think of. I'd genuinely love to hear what it catches.

You can't command an LLM. But you can get a promise out of it, and you can check. Let's build like it.

---

*The [promise-driven-agentic-kit](#) is open source under Apache-2.0. Start with the whitepaper, then open the clinic example. Corrections and extensions welcome — this is a living kit, and I mean that.*

*With gratitude to Mark Burgess and Jan Bergstra, whose Promise Theory is the foundation this is built on, and to the FizzBee project for the model checker that makes the proofs run.*
