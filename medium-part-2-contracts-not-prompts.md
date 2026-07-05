# Contracts, Not Prompts: How to Build an Agent You Can Prove

### Part 2 of 2. The runnable method: a model-checked contract, enforcement code that keeps a stochastic promiser honest, and a promise graph, so your agent can't reach a state it must never be in. With two runnable examples.

*By Jeremy Schulman*

---

This is the second of two pieces, and it's the *how*. The first, [Promises, Promises — Why Should You Believe?](#), made the case; here I'll compress that case into a few sentences so we can get straight to building.

An LLM is an autonomous, stochastic agent. You cannot command it. You can only elicit a promise and then *assess* whether it was kept. *Trust, but verify.* I've watched this shape work before, in another field: you hand an autonomous actor scoped authority, and put a deterministic guarantee beneath it so it cannot cause harm, no matter what it tries. (I tell that whole story in the first piece: Puppet, networks, and a physicist named Mark Burgess whose Promise Theory underpins all of this.) The trouble is that most write-ups land the reframe and then leave you staring at a blank file. Where does the promise *live?* What file is it in? How do you check it?

This piece answers that. I spent the last year building the answer into a runnable open-source kit: `<Github repo: TBD>`. We'll work through it with **The Clinic**, an appointment agent that provably cannot book before it verifies you, or double-book a slot. Not because a prompt asked nicely, but because the design makes those states unreachable, and I can prove it before I deploy. Let me show you the bridge. There are only a handful of moving parts, and none of them are exotic.

## One artifact, three readers

Here's the move that made everything click. Instead of a prose prompt, each agent's *entire* instruction set becomes a single document. I call it a **contract.** And the trick is that this one document is read by three different consumers, each taking what it needs:

1. a **model checker,** which proves the agent can never reach a bad state,
2. the **code that builds the agent,** which reads its declared promises, and
3. the **LLM itself,** which reads the whole thing as its operating instructions.

One artifact. Three readers. Same bytes. That last part matters more than it sounds, and I'll come back to it.

At the center of the contract is a small **state machine,** written in a language called [FizzBee](https://fizzbee.io). It's in the TLA+ family of formal specification languages, but with a Python-ish syntax that reads approachably. Here's the actual rule from **The Clinic**, the clinic-appointment assistant that's one of two runnable example agents in the kit (and a clean, shareable stand-in for the production systems I can't put on the page), verbatim:

```fizz
atomic action VerifyPatient:
    require not patient_verified
    require active_workflow == NO_WORKFLOW
    patient_verified = oneof [True, False]

always assertion PatientVerifiedBeforeWorkflow:
    return active_workflow == NO_WORKFLOW or patient_verified
```

You don't need to know FizzBee to read that. In plain English:

- An **action** is something the agent can do. The **require** lines are *guards*, the preconditions. `VerifyPatient` can only run when the patient isn't yet verified and no workflow is active.
- `oneof [True, False]` says the outcome is uncertain: verification might succeed or fail.
- An **always assertion** is an *invariant*, something that must be true in **every** reachable state. `PatientVerifiedBeforeWorkflow` says: either no workflow is running, or the patient is verified. There is no legal state where a workflow runs on an unverified patient. Full stop.

Now the payoff. A **model checker** takes that machine and explores *every reachable combination of states* the actions can produce, and confirms no invariant is ever broken. I run it offline, in CI, before anything ships:

```
[PASS] book_appointment
[PASS] clinic_orchestrator
[PASS] manage_appointment
3/3 contract(s) passed model checking.
```

This is the question a prose prompt can never answer: *"can it ever reach a bad state?"* Now it's answered. Not with "probably not." With **"no, and here's the exhaustive proof."** The model checker proves it at design time, before an LLM or a user is anywhere near it: the agent cannot reach a state it must never be in.

And this is not a toy that only passes because I wrote it to pass. My second example is the Trials of the Holy Grail (yes, the Monty Python one, knights and the Bridge of Death and the Knights Who Say "Ni!") with a Quest Marshal that should grant the Grail quest only after *both* trials are passed. **Its first draft failed model-checking.** The checker found a sequence I never would have: a knight could re-attempt a trial he'd already passed, fail it *after* the Grail was granted, and blow the invariant. The tool handed me the exact step-by-step trace to the bad state. The fix, making a passed trial "sticky," took two minutes. That's a real bug, caught by exhaustive search, before any human or any model ever touched the agent. Prose could never have caught it.

Now, "same bytes." In the usual setup (a state machine coded in one place, a prompt written in another) the machine and the instructions are *two different artifacts that drift.* You fix one, forget the other, and find out in production. Here, the state machine the checker proves and the instructions the model reads are **the same document.** They can't drift, because there's nothing to drift from.

## Formalize the structure, leave judgment to prose

I am *not* telling you to formalize your whole agent. That way lies madness. The single most useful rule I found is about where to draw the line:

> **Formalize structure and ordering. Leave judgment and phrasing to prose.**

"Verify before you book," "never double-book," "at most one task suspended at a time" are structural. They're about ordering and safety, and they belong in the model-checked state machine, because prose lets them drift.

But "is this message a greeting or a booking request?" is not a formal property and never will be. Neither is "how do I phrase this hand-off warmly?" That's judgment. It stays in prose, in a section of the contract I call step-guidance, right beside the formal parts but clearly quarantined from them.

Don't try to formalize the fuzzy stuff; you'll fail and hate your life. Don't leave the structural stuff to prose; it'll drift and hurt you. Getting that line right is most of the skill.

## The part you cannot skip

Now the biggest caveat, because it's the thing that separates a real contract from theater.

**Model-checking proves the specification. It does not prove the LLM follows the specification.**

The proof certifies that the *state machine* can't reach a bad state. It says nothing about whether your stochastic model actually stays on the legal path. The model can still misread eligibility, skip a guard, or fabricate an argument. If you model-check your contract, ship it as a prompt, and stop there, you've bought false confidence, which is worse than none.

Promise Theory explains why in one line: *a promise from an unreliable promiser is worthless to you without independent assessment.* And this is exactly what "Junos guarantees at the OS level" was doing all along: it never trusted the automation reaching in to make changes; it enforced the boundary underneath, no matter what that automation tried. So every safety invariant gets a twin. Take the no-double-book rule:

```fizz
always assertion NoDoubleBook:
    return (not appointment_booked) or slot_available
```

That invariant is the LLM's *promise:* "I'll never book a taken slot." The **assessment** is real code. The scheduling service itself refuses to commit a slot that isn't open, no matter what the model says. The model can promise all day; the code is what decides whether the promise was kept, and quietly refuses when it wasn't.

This LLM-promise-plus-code-assessment pair is, to me, the atomic unit of the whole method. **Never a stochastic promise standing alone. Always a stochastic promise backed by a deterministic guarantee.** The model check proves the map is coherent; the code polices the territory. You need both, and the code half is not optional.

## From one agent to a system of agents

Everything so far makes a *single* agent trustworthy. But The Clinic isn't one agent. It's a small society of them behind one friendly face: an orchestrator that verifies you and routes your request, a booking subagent, a subagent that cancels and reschedules, plus non-LLM service agents for the schedule, the insurance check, and the patient registry.

Draw a boundary around that whole society and treat it as one agent making a single promise to the patient (*"I'll book your appointment"*), and you have what Promise Theory calls a **superagent**: one face to the outside, a promise graph within. Mark Burgess's rule is that *"we may choose the boundary of an agent wherever we please,"* and that freedom is the point. The patient talks to one agent; inside, it's a society.

This is where I think Promise Theory earns its keep most, because multi-agent systems rot in the same place every time: **hidden dependencies.** One agent writes some shared state, another silently reads it, and nobody declared the handoff. It works until it doesn't. (Networking people: this is the "pinprick of death" all over again, a thousand tiny uncoordinated changes.)

Promise Theory drags every one of those dependencies into the open using two polarities. An agent makes an **offer** (`+`), "I will provide this," or a **use** (`−`), "I will accept and use that." Both are promises; the `−` is not mere dependence, it's an agent promising to accept what another offers. And the rule that does the work: cooperation only *binds* when a `+` offer meets a matching `−` use. An offer nobody uses, or a use nothing offers, is a **design defect you can detect mechanically.**

Each agent publishes a small manifest of its offers and uses. Here's the booking agent promising not to double-book, written as an offer:

```xml
<offer id="never_double_book" type="invariant" to="patient clinic-compliance">
  <body>A slot is never booked twice; the commit is refused by the provider
    schedule if the slot was taken since it was offered (NoDoubleBook, kept in
    code regardless of the model).</body>
</offer>
```

Notice the body names its own division of labor: the LLM promises it, the schedule service *keeps* it. Promise-and-assess, made explicit for anyone reading the manifest.

Three consequences fall out of this, and they're why I now design this way:

**The orchestrator owns nothing.** This one took me a while to fit my brain. Under the autonomy axiom, the orchestrator *cannot* promise that a subagent will book anything. It can only promise *its own* behavior: verify the patient, classify intent, relay to the subagent whose offer matches, remember at most one suspended task, relay the result. Routing stops being a *command* and becomes **selection among published offers.** The orchestrator never reaches inside a subagent to make it act; it uses the subagent's conditional offer, and the subagent's own guards are the real gate. If the subagent refuses, the orchestrator relays the refusal; it doesn't override it. (That's RBAC thinking, "who can do what," grown into a full graph.)

**Shared state becomes an agent.** Instead of a blackboard the orchestrator scribbles on and the subagents peek at, the patient registry is its *own* agent that publishes the verified patient; consumers declare that they rely on it. The invisible dependency becomes a declared, checkable binding, impossible to forget when you add a third workflow six months later.

**The whole graph is verified offline.** Just as the state machines get model-checked, the promise manifests get checked for completeness: every `−` use meets a `+` offer, and every condition is either met by some agent's offer or explicitly self-assessed. An agent relying on something nobody promised is a **build failure, not a 2 a.m. surprise.**

So the wager scales. For one agent it was *"can this reach a bad state?"* For the superagent it becomes *"can this society of agents make a promise it has no way to keep?"* And I answer that before I deploy, too.

I believe engineers building serious systems must have **choice and control**: choice of tools, frameworks, and languages, and control over how they build, deploy, and evolve. Any method worth adopting has to honor that instead of locking you in. So the property I care about most here isn't a feature at all; it's that the method asks nothing of your stack. The two examples prove it: The Clinic and the Trials of the Holy Grail run on **entirely different frameworks** (The Clinic on Google's ADK, the Trials on Pydantic AI) yet they share the *same* contracts and the *same* enforcement code. The only meaningful difference between them is a single file wiring each to its runtime. Everything that makes them *safe* is identical and framework-independent. The method lives in the contracts and the assessment code, not in anybody's framework-of-the-month. Choose your tools; keep your guarantees.

## What you actually walk away with

I don't want to leave you with a vibe. Here's the distilled standard I now hold my own agents to. If you build nothing else from this article, run your current design past these:

1. **Treat every model as an autonomous agent.** Design for elicited promises and mandatory assessment, not compliance. This ends the "why won't it obey?" spiral, because you stop expecting obedience.
2. **Make each agent's self-promises a model-checked contract.** Formalize ordering and safety as a state machine; prove it exhaustively offline. Keep judgment in prose, quarantined so it can't corrupt the guarantees.
3. **Every condition names who satisfies it.** No hidden dependencies. A condition is either self-assessed or met by a named agent's offer.
4. **Pair every stochastic promise with a deterministic guarantee.** The enforcement code isn't belt-and-suspenders. It's the whole point. Never ship the contract without it.
5. **Declare what you rely on; forbid unmatched edges.** Every use meets an offer. Relying on something nobody promised is a build failure.
6. **Derive the outside promise from the inside.** A superagent, a society of agents behind one face, must generate what it advertises to the world from what its members actually offer, so it can never overstate what it delivers.

Points 1–2 make a single agent trustworthy; that's where most teams stop, if they get there at all. Points 3–6 make a *system* trustworthy. And I genuinely believe this is where agentic engineering is heading, whether or not anyone uses the word "promise," because the premise underneath it is simply *true:* the model is an autonomous stochastic agent, and autonomous agents can only be promised, then assessed.

## When *not* to do this

I'd be doing you a disservice if I pretended this is free. It isn't, and knowing where it *doesn't* pay off is part of using it well.

A formal contract is more work than a paragraph. It costs tokens every turn, because it rides in the context window. It asks your team to read a state machine and run a model checker in CI. And I'll say it again, because it's the trap: the model check proves the spec, not the behavior, so the enforcement code is mandatory, which is *more* engineering, not less.

So **skip it** for one-shot Q&A, a single-tool lookup, or a throwaway prototype where a wrong turn costs nothing. There, a good prose prompt is exactly the right tool and a contract is just ceremony.

**Reach for it** when you've got multi-step workflows, ordering or safety constraints that truly must hold, actions involving money or identity or anything irreversible, and a system you need to evolve without quietly regressing. That's precisely the situation where "probably not, but I can't prove it" isn't good enough, and it's the situation I keep finding myself in.

## Looking back over the bridge

We've walked the whole method now: the contract that three readers share, the model check that proves the bad states unreachable, the enforcement code that keeps a promise against a stochastic promiser, and the promise graph that scales it all up to a superagent.

Strip away the machinery and one shape remains, and it's the same shape I first met in 2013. An autonomous actor, handed scoped authority, made safe not by trust but by a guarantee underneath. Then the actor was a config-management agent and the guarantee lived in the OS. Now the actor is an LLM and the guarantee lives in a model-checked contract and its enforcement code. Same idea. New actor. That's the whole reason I'm confident this is a real shift and not a fashion: I've watched this exact pattern cross a boundary from a neighboring discipline once already, and I've spent thirteen years living inside the field it remade.

The prize I promised at the very top, The Clinic that *provably cannot* book before you're verified, isn't a trick of a clever prompt. It's the payoff of that shape, made concrete: the contract makes the bad states unreachable, the code makes every promise assessed, and the promise graph makes every dependency something we declared out loud.

I packaged the whole thing as an open-source kit: the two runnable examples, the schemas, a project template that scaffolds a new contract-driven agent that's green out of the box, and an authoring skill that walks you through writing your first contract. You can model-check the examples *and talk to them.*

So here's my ask: go try it. Take a small, stateful agent you already have, one where a wrong turn actually costs something, and write its rules as a contract instead of a prompt. Run the model checker. Watch it find the state you didn't think of. Then come tell me what it caught.

So, why should you believe? You shouldn't. Not a promise from a stochastic machine, and honestly, not one from me either. This is where *trust, but verify* earns its keep, with one word removed: you come to trust an agent *by* verifying it, in code, over and over. Trust *by* verify. You can't command an LLM. You can only get a promise out of it, and then prove it's kept. That was the "Ah, Ha!" This is the "Cha, Ching!"

I've bet on this shape before. I'm betting on it again, and this time, I'd love for you to build it with me.

---

*The [promise-driven-agentic-kit](#) is open source under Apache-2.0. Start with the whitepaper, then open The Clinic example. Corrections and extensions welcome; this is a living kit, and I mean that.*

*With deep gratitude to Mark Burgess, whose Promise Theory is the foundation everything here is built on: his* [Book of Promises](http://markburgess.org/BookOfPromises.pdf) *(the full* Promise Theory: Principles and Applications*, with Jan Bergstra, free to read online) and the more approachable* Thinking in Promises *(O'Reilly). Thanks, too, to the FizzBee project for the model checker that makes the proofs run.*
