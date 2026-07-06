# Contracts, Not Prompts: How to Build an Agent You Can Prove

### The runnable method: a model-checked contract, enforcement code that keeps a stochastic promiser honest, and a promise graph, so your agent can't reach a state it must never be in. With two runnable examples.

*By Jeremy Schulman · Part 2 of 2*

---

This is the second of two pieces. The first, [Promises, Promises — Why Should You Believe?](#), argued the *why*: you cannot command an LLM, you can only elicit a promise and then *assess* it. *Trust, but verify.* This piece shows you the *how*.

This approach is for software engineers building **complex, multi-agent
workflow** solutions: systems where many AI agents cooperate to carry a real
business process from end to end. If you are developing a single-turn chatbot,
it is overkill. For the types of autonomous BPA solutions I build, it is
essential.

Does this sound like you?

> *As a software engineer evolving our business-process automation into the era of AI, I need to build systems where many AI agents work together to carry out complex, multi-step workflows, reliably enough to run the business on.*

Reliability is the whole game. 

This article introduces a kit you build *with*, not one you run. It is not
_yet another agentic framework_ (YAAF). There are some code examples you can
run and play around with. The idea is that you use this kit to code agents,
either in the "artisanal" way or with your favorite code assistant.

**TL;DR:** if you just want to look at a GitHub repo: `<Github repo: TBD>`.

The repo includes an example, **The Clinic**.  I will show you the appointment
agent that provably cannot book before it verifies a patient, or double-book a
slot. Not because a prompt asked nicely, but because the design makes those
states unreachable, and I can prove it before I deploy.

## `Contract` - One Artifact for Software Lifecycle

Here's the move that made everything click. Instead of a prose prompt, an agent's *entire* instruction set becomes a single document. I call it a **contract.** You author it once, then carry that same document through every stage of building the system: Design, Build, and Run.

![One contract across the AI development lifecycle. Design: the FizzBee model checker reads it and returns a verdict, either PASS or a counterexample showing the exact path to a bad state. Build: your AI coding assistant reads it to generate the agent and its enforcement code. Run: the LLM executes inside any agentic framework, with the enforcement code assessing every action. Proven at design, enforced at runtime.](images/contract-lifecycle.png)

One document, three stages, same bytes. That last part matters more than it sounds, and I'll come back to it. The rest of this piece walks that lifecycle, one stage at a time.

## Design — capture the workflow, and prove it

**Why a state machine, and why you don't have to think in one.** You're probably not starting from a blank page. You're staring at a workflow that already exists and creaks: a tangle of Zapier zaps, a Workato recipe, or some bespoke in-house automation that's been patched for years and that everyone is afraid to touch. And you probably don't think of that workflow as a *state machine.* Almost no one does.

You don't have to. That workflow already *is* a state machine, whether anyone ever drew it: it has states, transitions between them, and states it must never enter. The machine is latent in the process; someone just has to capture it.

And that someone isn't you, at least not by hand. It works like hiring a lawyer: you don't arrive knowing the statutes or how to word the clauses; you describe what you need, you go back and forth, and the lawyer turns the conversation into a contract that holds up. Here it is the same shape. You express the workflow's intent to an AI coding assistant, refine it through Q&A, and the assistant, which knows the contract's schema, drafts the whole thing, the FizzBee state machine included. Your job is to know the workflow. The assistant's job is to render it as a contract. FizzBee's job is to capture its essence precisely, in a form a machine can check.

So let's look at what it drafts. Here, verbatim, is the heart of **The Clinic**'s contract: its state machine, written in [FizzBee](https://fizzbee.io), a formal-methods language in the TLA+ family with an approachable, Python-ish syntax. (The Clinic is one of the kit's two runnable examples, a shareable stand-in for the production systems I can't show.)

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

This is the question a prose prompt can never answer: *can it ever reach a bad state?* The failures that actually hurt an agent are not bad answers, they are bad *states*: booked before verified, double-booked, access granted without authorization. And you cannot test your way to *ever*. The space of conversations is effectively infinite and the model is nondeterministic, so no suite of examples ever covers the one path that bites you in production. A model checker does what testing cannot: it walks *every reachable state* and either proves the forbidden ones unreachable or hands you the exact steps that reach one. It is the adversarial read every contract needs, the one that finds the loophole nobody thought to look for. So the answer is no longer "probably not." It is **"no, and here's the exhaustive proof,"** at design time, before an LLM or a user is anywhere near it. That proof is the keystone of the whole method: structure alone, YAML or a tidy prompt, makes an agent *neater*; only a proof makes it *provable*.

And this is not a toy that only passes because I wrote it to pass. My second example is the Trials of the Holy Grail (yes, the Monty Python one, knights and the Bridge of Death and the Knights Who Say "Ni!") with a Quest Marshal that should grant the Grail quest only after *both* trials are passed. **Its first draft failed model-checking.** The checker found a sequence I never would have: a knight could re-attempt a trial he'd already passed, fail it *after* the Grail was granted, and blow the invariant. The tool handed me the exact step-by-step trace to the bad state. The fix, making a passed trial "sticky," took two minutes. That's a real bug, caught by exhaustive search, before any human or any model ever touched the agent. Prose could never have caught it.

And here is the part that quietly changes your day. That counterexample is not a stack trace you squint at; it is machine-readable feedback. Point your AI coding assistant at a failing `fizz` run and it reads the trace, repairs the contract, and re-runs, closing the loop on its own until the design is green. Verification stops being a chore and becomes a tight author-check-fix cycle. It is the lawyer again, mid-draft: the model checker flags the exact clause that would fail, and your assistant redlines the contract and refiles, until it holds.

![The Design loop: you and your AI coding assistant author the contract; fizz checks it and returns PASS or a counterexample naming the exact path to a bad state; the assistant reads the counterexample, repairs the contract, and re-runs until it passes.](images/design-loop.png)

**Where to draw the line.** I am *not* telling you to formalize your whole agent. That way lies madness. The most useful rule I found is about where the formal part stops:

> **Formalize structure and ordering. Leave judgment and phrasing to prose.**

"Verify before you book," "never double-book," "at most one task suspended at a time" are structural. They are about ordering and safety, and they belong in the model-checked state machine, because prose lets them drift.

But "is this message a greeting or a booking request?" is not a formal property and never will be. Neither is "how do I phrase this hand-off warmly?" That is judgment. It stays in prose, in a section of the contract I call step-guidance, right beside the formal parts but clearly quarantined from them.

Don't try to formalize the fuzzy stuff; you'll fail and hate your life. Don't leave the structural stuff to prose; it'll drift and hurt you. Getting that line right is most of the skill.

So how do the FizzBee half and the Promise Theory half actually fit together? They are not two tools bolted side by side. They are the *same guarantee*, showing up at each stage of the lifecycle. Follow one, `patient_verified`, from Design through Run.

**In Design, the model checker reads it as a proof.** The invariant `PatientVerifiedBeforeWorkflow` says no workflow may run for an unverified patient, and the checker proves that holds in every reachable state.

**In Build, the builder reads it as a promise.** In the contract's `<promises>` section, the same guarantee appears as a declared offer, carrying a condition with the *same token*:

```xml
<offer id="relay_to_matching_offer" type="workflow" to="patient">
  <body>Relay a booking, cancel, or reschedule request to the subagent whose
    published offer matches.</body>
  <condition ref="patient_verified"/>
</offer>
```

That `patient_verified` is not a naming coincidence. It is literally the variable the model checker just reasoned about. This is the hinge of the whole design. Promise Theory does not compete with the state machine; it *names* what the invariant means, a promise made to a promisee, in a vocabulary that other agents can declare they depend on.

**At Run, the LLM reads it as an instruction.** The same guarantee once more, in the prose it follows at runtime: never start a workflow before the patient is verified.

One guarantee, one vocabulary, carried through every stage. That is the answer to the question I get most often: FizzBee and Promise Theory are not two systems you keep in sync. They are two readings of one contract, tied by a single shared name, with FizzBee supplying the proof and Promise Theory the meaning that lets agents compose. That shared document is the whole point.


Now, "same bytes." In the usual setup (a state machine coded in one place, a prompt written in another) the machine and the instructions are *two different artifacts that drift.* You fix one, forget the other, and find out in production. Here, the state machine the checker proves and the instructions the model reads are **the same document.** They can't drift, because there's nothing to drift from.

That property isn't new, and it isn't really mine. A single declarative source of truth, with everything else derived from it, is the discipline behind intent-based networking, which I came up through years ago (that story is in the first piece). Here the source is a contract rather than a network design, but the rule is identical: change the one source, and everything downstream follows. Nothing drifts.

## Build — give the contract teeth

Design handed you a proven contract. Build turns it into a running agent, and here is the catch that separates a real contract from theater.

**Model-checking proves the specification. It does not prove the LLM follows it.**

The proof certifies that the *state machine* can't reach a bad state. It says nothing about whether your stochastic model actually stays on the legal path. The model can still misread eligibility, skip a guard, or fabricate an argument. If you model-check your contract, ship it as a prompt, and stop there, you've bought false confidence, which is worse than none.

This is where a contract needs *teeth.* A legal contract nobody will enforce is just a wish, and a proven agent contract with nothing behind it is no different. Promise Theory says it in one line: *a promise from an unreliable promiser is worthless to you without independent assessment.* And this is exactly what "Junos guarantees at the OS level" was doing all along: it never trusted the automation reaching in to make changes; it enforced the boundary underneath, no matter what that automation tried. So every safety invariant gets a twin. Take the no-double-book rule:

```fizz
always assertion NoDoubleBook:
    return (not appointment_booked) or slot_available
```

That invariant is the LLM's *promise:* "I'll never book a taken slot." The **assessment** is real code. The scheduling service itself refuses to commit a slot that isn't open, no matter what the model says. The model can promise all day; the code is what decides whether the promise was kept, and quietly refuses when it wasn't.

This LLM-promise-plus-code-assessment pair is, to me, the atomic unit of the whole method. **Never a stochastic promise standing alone. Always a stochastic promise backed by a deterministic guarantee.** The model check proves the map is coherent; the code polices the territory. You need both, and the code half is not optional. The model check is what makes the design *provable*; the enforcement code is what makes the running agent *trustworthy*.

![The Build stage: your AI coding assistant reads the contract and produces the running agent, its framework wiring plus the enforcement code that gives every promise teeth.](images/build-stage.png)

## Run — the agent acts, inside its guarantees

Now the agent is live, and the runtime posture is the opposite of hope. A request comes in; the LLM follows the contract's prose and proposes an action, a tool call, a hand-off. Before anything happens, the enforcement code assesses that proposal against the invariants. Keep the promise, and it runs. Break one, and it is refused.

That refusal is not an error to swallow. It is a first-class outcome: a structured result naming the condition that failed ("slot no longer available," "patient not verified"), which the agent relays to the user or recovers from. Autonomy includes the right to say no, and a clean no beats a confident, wrong yes.

So the LLM stays free to *propose* anything, and being stochastic, sometimes it will. It can never *do* the wrong thing, because the deterministic layer beneath it will not pass a broken promise. This is the lawyer's contract in force: drafted and proven in Design, given teeth in Build, and now, at Run, any move that would breach it simply does not happen.

![The Run stage: a user request reaches the LLM in any framework, which proposes an action; the enforcement code assesses it against the contract and either executes it or returns a structured refusal. The agent acts freely, but never past its guarantees.](images/run-stage.png)

## From one agent to a system of agents

Everything so far makes a *single* agent trustworthy. But The Clinic isn't one agent. It's a small society of them behind one friendly face: an orchestrator that verifies you and routes your request, a booking subagent, a subagent that cancels and reschedules, plus non-LLM service agents for the schedule, the insurance check, and the patient registry.

Draw a boundary around that whole society and treat it as one agent making a single promise to the patient (*"I'll book your appointment"*), and you have what Promise Theory calls a **superagent**: one face to the outside, a promise graph within. Mark Burgess's rule is that *"we may choose the boundary of an agent wherever we please,"* and that freedom is the point. The patient talks to one agent; inside, it's a society. Think of a firm: one name on the door, many parties bound by their own agreements inside.

This is where I think Promise Theory earns its keep most, because multi-agent systems rot in the same place every time: **hidden dependencies.** One agent writes some shared state, another silently reads it, and nobody put the handshake in writing. It works until it doesn't. (Networking people: this is the "pinprick of death" all over again, a thousand tiny uncoordinated changes.)

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

**The orchestrator owns nothing.** This one took me a while to fit my brain. Under the autonomy axiom, the orchestrator *cannot* promise that a subagent will book anything. It can only promise *its own* behavior: verify the patient, classify intent, relay to the subagent whose offer matches, remember at most one suspended task, relay the result. Routing stops being a *command* and becomes **selection among published offers.** The orchestrator is a general contractor who cannot pour the concrete or force a subcontractor's hand; it can only rely on the offer each subagent signed, and that subagent's own guards are the real gate. If the subagent refuses, the orchestrator relays the refusal; it doesn't override it. In Promise Theory terms, every agent signs only for itself. (That's RBAC thinking, "who can do what," grown into a full graph.)

**Shared state becomes an agent.** Instead of a blackboard the orchestrator scribbles on and the subagents peek at, the patient registry is its *own* agent that publishes the verified patient; consumers declare that they rely on it. The invisible dependency becomes a declared, checkable binding, impossible to forget when you add a third workflow six months later.

**The whole graph is verified offline.** Just as the state machines get model-checked, the promise manifests get checked for completeness: every `−` use meets a `+` offer, and every condition is either met by some agent's offer or explicitly self-assessed. An agent relying on something nobody promised is a **build failure, not a 2 a.m. surprise.**

So the wager scales. For one agent it was *"can this reach a bad state?"* For the superagent it becomes *"can this society of agents make a promise it has no way to keep?"* And I answer that before I deploy, too.

I believe engineers building serious systems must have **choice and control**: choice of tools, frameworks, and languages, and control over how they build, deploy, and evolve. Any method worth adopting has to honor that instead of locking you in. So the property I care about most here isn't a feature at all; it's that the method asks nothing of your stack. The two examples prove it: The Clinic and the Trials of the Holy Grail run on **entirely different frameworks** (The Clinic on Google's ADK, the Trials on Pydantic AI) yet they share the *same* contracts and the *same* enforcement code. The only meaningful difference between them is a single file wiring each to its runtime. Everything that makes them *safe* is identical and framework-independent. The method lives in the contracts and the assessment code, not in anybody's framework-of-the-month. Choose your tools; keep your guarantees.

## What you actually walk away with

I don't want to leave you with a vibe. Here's the distilled standard I hold my own systems to, mapped to the lifecycle we just walked. If you build nothing else from this piece, run your design past these:

1. **Treat every model as an autonomous agent.** Design for elicited promises and mandatory assessment, not compliance. This ends the "why won't it obey?" spiral, because you stop expecting obedience.
2. **Make each agent's self-promises a model-checked contract.** *(Design.)* Formalize ordering and safety as a state machine; prove it exhaustively offline. Keep judgment in prose, quarantined so it can't corrupt the guarantees.
3. **Every condition names who satisfies it.** *(Design.)* No hidden dependencies. A condition is either self-assessed or met by a named agent's offer.
4. **Pair every stochastic promise with a deterministic guarantee.** *(Build.)* The enforcement code isn't belt-and-suspenders. It's the whole point. Never ship the contract without it.
5. **Make refusal first-class.** *(Run.)* A structured "no" that names the unmet condition is a normal outcome, relayed and recorded, not an exception to swallow.
6. **Declare what you rely on; forbid unmatched edges.** *(Compose.)* Every use meets an offer. Relying on something nobody promised is a build failure.
7. **Derive the outside promise from the inside.** *(Compose.)* A superagent, a society of agents behind one face, must generate what it advertises to the world from what its members actually offer, so it can never overstate what it delivers.

Points 1 through 5 make a single agent trustworthy, from Design through Run; points 6 and 7 make a *system* trustworthy as you compose. And I genuinely believe this is where agentic engineering is heading, whether or not anyone uses the word "promise," because the premise underneath it is simply *true:* the model is an autonomous stochastic agent, and autonomous agents can only be promised, then assessed.

## When *not* to do this

I'd be doing you a disservice if I pretended this is free. It isn't, and knowing where it *doesn't* pay off is part of using it well.

A formal contract is more work than a paragraph. It costs tokens every turn, because it rides in the context window. It asks your team to read a state machine and run a model checker in CI. And I'll say it again, because it's the trap: the model check proves the spec, not the behavior, so the enforcement code is mandatory, which is *more* engineering, not less.

So **skip it** for one-shot Q&A, a single-tool lookup, or a throwaway prototype where a wrong turn costs nothing. There, a good prose prompt is exactly the right tool and a contract is just ceremony.

**Reach for it** when you've got multi-step workflows, ordering or safety constraints that truly must hold, actions involving money or identity or anything irreversible, and a system you need to evolve without quietly regressing. That's precisely the situation where "probably not, but I can't prove it" isn't good enough, and it's the situation I keep finding myself in.

## Looking back over the bridge

We've walked the whole method now: the contract that every stage reads, the model check that proves the bad states unreachable, the enforcement code that keeps a promise against a stochastic promiser, and the promise graph that scales it all up to a superagent.

Strip away the machinery and one shape remains, and it's the same shape I first met in 2013. An autonomous actor, handed scoped authority, made safe not by trust but by a guarantee underneath. Then the actor was a config-management agent and the guarantee lived in the OS. Now the actor is an LLM and the guarantee lives in a model-checked contract and its enforcement code. Same idea. New actor. That's the whole reason I'm confident this is a real shift and not a fashion: I've watched this exact pattern cross a boundary from a neighboring discipline once already, and I've spent thirteen years living inside the field it remade.

The prize I promised at the very top, The Clinic that *provably cannot* book before you're verified, isn't a trick of a clever prompt. It's the payoff of that shape, made concrete: the contract makes the bad states unreachable, the code makes every promise assessed, and the promise graph makes every dependency something we declared out loud.

I packaged all of this as the **promise-driven-agentic-kit**. It isn't an app you run; it's a set of files you build *with*, in Python. It ships two complete worked examples you *can* run and talk to (The Clinic and the Trials of the Holy Grail), the contract schemas, a template that scaffolds a fresh contract-driven agent that's green out of the box, and agentic-coding **Skills** you fold into your own workflow to author and model-check contracts as you go.

So here's my ask: go try it. Take a small, stateful agent you already have, one where a wrong turn actually costs something, and write its rules as a contract instead of a prompt. Run the model checker. Watch it find the state you didn't think of. Then come tell me what it caught.

So, why should you believe? You shouldn't. Not a promise from a stochastic machine, and honestly, not one from me either. This is where *trust, but verify* earns its keep, with one word removed: you come to trust an agent *by* verifying it, in code, over and over. Trust *by* verify. You can't command an LLM. You can only get a promise out of it, and then prove it's kept. That was the "Ah, Ha!" This is the "Cha, Ching!"

I've bet on this shape before. I'm betting on it again, and this time, I'd love for you to build it with me.

---

*The [promise-driven-agentic-kit](#) is open source under Apache-2.0. Start with the whitepaper, then open The Clinic example. Corrections and extensions welcome; this is a living kit, and I mean that.*

*With deep gratitude to Mark Burgess, whose Promise Theory is the foundation everything here is built on: his* [Book of Promises](http://markburgess.org/BookOfPromises.pdf) *(the full* Promise Theory: Principles and Applications*, with Jan Bergstra, free to read online) and the more approachable* Thinking in Promises *(O'Reilly). Thanks, too, to the FizzBee project for the model checker that makes the proofs run.*
