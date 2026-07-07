# Everybody Wants to Rule the World

### How to build an agent you can prove. The runnable method for a single agent: a contract you can prove at design time and enforce at runtime, so it can't reach a state it must never be in.

*By Jeremy Schulman · Part 2 of 3*

---

This is the second of three pieces. The first, [Promises, Promises — Why Do I Believe?](#), argued the *why*: you cannot command an LLM, you can only elicit a promise and then *assess* it. *Trust, but verify.* This piece shows you the *how*.

This approach is for software engineers building **complex, multi-agent
workflow** solutions: systems where many AI agents cooperate to carry a real
business process from end to end. If you are developing a single-turn chatbot,
this approach is overkill. For the types of autonomous BPA solutions I build, it
is essential. This piece teaches the method on a single agent — the clearest way
to see it work; wiring many of them into one system is the finale, Part 3.

Does this sound like you?

> *As a software engineer evolving our business-process automation into the era of AI, I need to build systems where many AI agents work together to carry out complex, multi-step workflows, reliably enough to run the business on.*

Reliability is the whole game. 

This article introduces a kit you build *with*, not one you run. It is not
_yet another agentic framework_ (YAAF). There are some code examples you can
run and play around with. The idea is that you use this kit to code agents,
either in the "artisanal" way or with your favorite code assistant.

**TL;DR:** if you just want to look at a GitHub repo: `<Github repo: TBD>`.

The repo includes an example, **The Clinic**. I will show you the appointment
agent that provably cannot book before it verifies a patient, or double-book a
slot. Not because a prompt asked nicely, but because the design makes those
states unreachable, and I can prove it before I deploy.

## From Intent to a Contract You Can Prove

Here's the move that made everything click. Instead of a prose prompt, an agent's *entire* instruction set becomes a single document. Let's say we call it a **contract** — I'm terrible at naming things, but it fits for now. Not *intent*, tempting as that word is where I come from: you don't impose intent on an autonomous agent, you strike a deal and hold it to the terms. You author it once, then carry that same document through every stage of building the system: Design, Build, and Run.

![One contract across the AI development lifecycle. Design: the FizzBee model checker reads it and returns a verdict, either PASS or a counterexample showing the exact path to a bad state. Build: your AI coding assistant reads it to generate the agent and its enforcement code. Run: the LLM executes inside any agentic framework, with the enforcement code assessing every action. Proven at design, enforced at runtime.](images/contract-lifecycle.png)

One document, three stages, same bytes. That last part matters more than it sounds, and I'll come back to it. Three isn't a magic number, either — it's just where I've taken this so far. Anything downstream that drifts from your code today could read the same contract instead: a generated design doc, an integration test plan, an onboarding guide. I haven't built those yet, but the single source is what makes them possible. The rest of this piece walks the three stages I *have* built, one at a time.

## Design — Capture the Workflow, and Prove It

You're probably not starting a design from a blank page. Engineers borrowed a word for this from construction: it's a *brownfield* — an existing, load-bearing, slightly contaminated thing — not a *greenfield* you build clean. Sometimes that brownfield is software: a tangle of Zapier zaps, a Workato recipe, some bespoke automation patched for years that everyone's afraid to touch. More often, though, it isn't software at all — it's a process a person runs by hand, following a runbook that lives in a wiki page or a senior employee's head. Either way, there's already a *design* buried in there — you've just never drawn it out. And you almost certainly don't think of that design as a *state machine.* Almost no one does.

You don't have to think in one, though. That design — which manifests as the workflow you run today — already *is* a state machine, whether anyone ever drew it: it has states, transitions between them, and states it must never enter. The machine is latent in the process; someone just has to capture it. That's the real nature of this work: it's brownfield modernization. The AI era doesn't get to start over, it inherits the process that already runs the business — and this method is how you re-express that process, faithfully, as something you can prove.

And that someone doesn't need to be you, at least not by hand. Capturing the design can work like hiring a lawyer: you don't arrive knowing the statutes or how to word the clauses; you describe what you need, you go back and forth, and the lawyer turns the conversation into a contract that holds up. Here, it's the same shape. You express the workflow's intent to an AI coding assistant, refine it through Q&A, and the assistant, which knows the contract's schema, drafts the whole thing, the FizzBee state machine included. Your job is to know the workflow. The assistant's job is to render it as a contract. FizzBee's job is to capture its essence precisely, in a form a machine can check.

So let's look at what the assistant drafts. Take the orchestrator — **The Clinic**'s front desk. On its own it's a ten-action state machine; here it is in full:

![The orchestrator's complete state machine: four states — Unverified, Verified · Idle, Workflow Active, and Pivot Pending — connected by its ten actions. The VerifyPatient transition is highlighted, and a dashed red edge marks the state the PatientVerifiedBeforeWorkflow invariant makes unreachable: running a workflow before the patient is verified.](images/orchestrator-state-machine.png)

We'll zoom in on just one of those ten actions and the single invariant it protects. Here, verbatim, is that slice, written in [FizzBee](https://fizzbee.io), a formal-methods language in the TLA+ family with an approachable, Python-ish syntax. (The Clinic is one of the kit's two runnable examples, a shareable stand-in for the production systems I can't show.)

![FizzBee source from the orchestrator: the VerifyPatient action, guarded so it can only run for an unverified patient with no active workflow, and the PatientVerifiedBeforeWorkflow invariant, which says no workflow runs unless the patient is verified.](images/code-fizz-verify.png)

You don't need to know FizzBee to read that. In plain English:

- An **action** is something the agent can do. The **require** lines are *guards*, the preconditions. `VerifyPatient` can only run when the patient isn't yet verified and no workflow is active.
- `oneof [True, False]` says the outcome is uncertain: verification might succeed or fail.
- An **always assertion** is an *invariant*, something that must be true in **every** reachable state. `PatientVerifiedBeforeWorkflow` says: either no workflow is running, or the patient is verified. There is no legal state where a workflow runs on an unverified patient. Full stop.

Now the payoff. A **model checker** takes that machine and explores *every reachable combination of states* the actions can produce, and confirms no invariant is ever broken. I run it offline, in CI, before anything ships:

![Model-checker output: PASS for book_appointment, clinic_orchestrator, and manage_appointment — 3 of 3 contracts passed model checking.](images/code-check-pass.png)

This is the question a prose prompt can never answer: *can the agent ever reach a bad state?* The failures that actually hurt an agent are not bad answers, they are bad *states*: booked before verified, double-booked, access granted without authorization. And you cannot test your way to *ever*. The space of conversations is effectively infinite and the model is nondeterministic, so no suite of examples ever covers the one path that bites you in production. A model checker does what testing cannot: it walks *every reachable state* and either proves the forbidden ones unreachable or hands you the exact steps that reach one. It is the adversarial read every contract needs, the one that finds the loophole nobody thought to look for. So the answer is no longer "probably not." It is **"no, and here's the exhaustive proof,"** at design time, before an LLM or a user is anywhere near it. That proof is the keystone of the whole method: structure alone, YAML or a tidy prompt, makes an agent *neater*; only a proof makes it *provable*.

And this is not a toy that only passes because I wrote it to pass. My second example is the Trials of the Holy Grail (yes, the Monty Python one, knights and the Bridge of Death and the Knights Who Say "Ni!") with a Quest Marshal that should grant the Grail quest only after *both* trials are passed. **Its first draft failed model-checking.** The checker found a sequence I never would have: a knight could re-attempt a trial he'd already passed, fail it *after* the Grail was granted, and blow the invariant. The tool handed me the exact step-by-step trace to the bad state. The fix, making a passed trial "sticky," took two minutes. That's a real bug, caught by exhaustive search, before any human or any model ever touched the agent. Prose could never have caught it.

And here is the part that quietly changes your day. That counterexample is not a stack trace you squint at; it is machine-readable feedback. Point your AI coding assistant at a failing `fizz` run and it reads the trace, repairs the contract, and re-runs, closing the loop on its own until the design is green. Verification stops being a chore and becomes a tight author-check-fix cycle. It is the lawyer again, mid-draft: the model checker flags the exact clause that would fail, and your assistant redlines the contract and refiles, until it holds.

![The Design loop: you and your AI coding assistant author the contract; fizz checks it and returns PASS or a counterexample naming the exact path to a bad state; the assistant reads the counterexample, repairs the contract, and re-runs until it passes.](images/design-loop.png)

**Where to draw the line.** I am *not* telling you to formalize your whole agent. That way lies madness. The most useful rule I found is about where the formal part stops:

> **Formalize structure and ordering. Leave judgment and phrasing to prose.**

"Verify before you book," "never double-book," "at most one task suspended at a time" are structural. They are about ordering and safety, and they belong in the model-checked state machine, because prose lets them drift.

But "is this message a greeting or a booking request?" is not a formal property and never will be. Neither is "how do I phrase this hand-off warmly?" That is judgment. It stays in prose, in a section of the contract I call step-guidance, right beside the formal parts but clearly quarantined from them.

Don't try to formalize the fuzzy stuff; you'll fail and hate your life. Don't leave the structural stuff to prose; it'll drift and hurt you. Getting that line right is most of the skill.

So how do the FizzBee half and the Promise Theory half actually fit together? One clarification first, because the names are misleading: FizzBee is an actual tool you run, but Promise Theory is not a library you install or a framework you import. It's a way of thinking about who promises what to whom (Mark Burgess's work; the *why* is in Part 1). In this method it manifests as exactly one concrete thing: the contract's `<promises>` section. So the two aren't tools bolted side by side. They are the *same guarantee*, showing up at each stage of the lifecycle. Follow one, `patient_verified`, from Design through Run.

**In Design, the model checker reads it as a proof.** The invariant `PatientVerifiedBeforeWorkflow` says no workflow may run for an unverified patient, and the checker proves that holds in every reachable state.

**In Build, the builder reads it as a promise.** In the contract's `<promises>` section, the same guarantee appears as a declared offer, carrying a condition with the *same token*:

![The relay_to_matching_offer offer from the contract's promises section: it relays a booking, cancel, or reschedule request to the subagent whose published offer matches, carrying a condition that refs patient_verified.](images/code-offer-relay.png)

That `patient_verified` is not a naming coincidence. It is literally the variable the model checker just reasoned about. This is the hinge of the whole design. Promise Theory does not compete with the state machine; it *names* what the invariant means, a promise made to a promisee, in a vocabulary that other agents can declare they depend on.

**At Run, the LLM reads it as an instruction.** The same guarantee once more, in the prose it follows at runtime: never start a workflow before the patient is verified.

One guarantee, one vocabulary, carried through every stage. That is the answer to the question I get most often: FizzBee and Promise Theory are not two systems you keep in sync. They are two readings of one contract, tied by a single shared name, with FizzBee supplying the proof and Promise Theory the meaning that lets agents compose. That shared document is the whole point.


Now, "same bytes." In the usual setup (a state machine coded in one place, a prompt written in another) the machine and the instructions are *two different artifacts that drift.* You fix one, forget the other, and find out in production. Here, the state machine the checker proves and the instructions the model reads are **the same document.** They can't drift, because there's nothing to drift from.

That property isn't new, and it isn't really mine. A single declarative source of truth, with everything else derived from it, is the discipline behind intent-based networking, which I came up through years ago (that story is in the first piece). Here the source is a contract rather than a network design, but the rule is identical: change the one source, and everything downstream follows. Nothing drifts.

## Build — Give the Contract Teeth

Design handed you a proven contract. Build turns it into a running agent.

![The Build stage: your AI coding assistant reads the contract and produces the running agent, its framework wiring plus the enforcement code that gives every promise teeth.](images/build-stage.png)

But here's the catch that separates a real contract from theater.

**Model-checking proves the specification. It does not prove the LLM follows it.**

The proof certifies that the *state machine* can't reach a bad state. It says nothing about whether your stochastic model actually stays on the legal path. The model can still misread eligibility, skip a guard, or fabricate an argument. If you model-check your contract, ship it as a prompt, and stop there, you've bought false confidence, which is worse than none.

This is where a contract needs *teeth.* A legal contract nobody will enforce is just a wish; what gives it force isn't the signatures on the page, it's knowing a court will hold you to them. A proven agent contract with nothing behind it is no different. Promise Theory says it in one line: *a promise from an unreliable promiser is worthless to you without independent assessment.* So every safety invariant gets a twin, the code that plays the court. Take the no-double-book rule:

![FizzBee invariant NoDoubleBook from the booking agent: an appointment is booked only if the slot was available.](images/code-fizz-nodoublebook.png)

That invariant is the LLM's *promise:* "I'll never book a taken slot." The **assessment** is real code, in the scheduling service itself, which refuses to commit a slot that isn't open, no matter what the model says:

![Python enforcement in services/schedule.py: the NoDoubleBook code twin. It looks up the slot and refuses to commit unless the slot exists and is still open, returning a structured refusal otherwise.](images/code-py-enforce.png)

The model can promise all day; this code is what decides whether the promise was kept, and returns a structured refusal when it wasn't. (That `refusal(...)` is the same first-class "no" that surfaces at Run, below.)

This LLM-promise-plus-code-assessment pair is, to me, the atomic unit of the whole method. **Never a stochastic promise standing alone. Always a stochastic promise backed by a deterministic guarantee.** The model check proves the map is coherent; the code polices the territory. You need both, and the code half is not optional. The model check is what makes the design *provable*; the enforcement code is what makes the running agent *trustworthy*.


## Run — The Agent Acts, Inside Its Guarantees

Now the agent is live, and the runtime posture is the opposite of hope. A request comes in; the LLM follows the contract's prose and proposes an action, a tool call, a hand-off. Before anything happens, the enforcement code assesses that proposal against the invariants. Keep the promise, and it runs. Break one, and it is refused.

![The Run stage: a user request reaches the LLM in any framework, which proposes an action; the enforcement code assesses it against the contract and either executes it or returns a structured refusal. The agent acts freely, but never past its guarantees.](images/run-stage.png)

That refusal is not an error to swallow. It is a first-class outcome: a structured result naming the condition that failed ("slot no longer available," "patient not verified"), which the agent relays to the user or recovers from. Autonomy includes the right to say no, and a clean no beats a confident, wrong yes.

So the LLM stays free to *propose* anything, and being stochastic, sometimes it will. It can never *do* the wrong thing, because the deterministic layer beneath it will not pass a broken promise. This is the lawyer's contract in force: drafted and proven in Design, given teeth in Build, and now, at Run, any move that would breach it simply does not happen.

## One Agent You Can Prove

That is one agent you can prove, and one you can trust, from Design through Run.

But a single agent is rarely the whole system. Look back at that state machine: the moment the orchestrator reaches `RouteToWorkflow`, it hands off to a *subagent* — a booking agent, or one that cancels and reschedules — and each of those is its own contract, with its own state machine and its own invariants, exactly like the one we just built. The Clinic is really a *society* of agents behind one friendly face. Getting many of them to cooperate without lying to each other is where most designs quietly fall apart, and where the promise graph finally earns its keep. That is the finale: [Games Without Frontiers — How to Compose a System You Can Prove](#).
