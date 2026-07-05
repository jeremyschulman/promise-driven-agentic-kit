# Promises, Promises — Why Should You Believe?

### You can't command an LLM. You can only elicit a promise and verify it. A 20-year-old theory, and a runnable way to build agents you can actually trust.

*By Jeremy Schulman*

---

I want this article to blow your mind. I know how that lands — it's a big promise, and you have no reason yet to believe it. Good. Hold onto that skepticism; it's the whole point, and we'll get there.

For over a year I've been building and shipping the hard kind of AI agent: stateful, multi-step, safety-sensitive systems that run real business workflows, where a wrong move actually costs something. Along the way I worked out a technique for building complex agentic systems that I haven't seen anywhere else. So I'm not talking hypotheticals — I'm going to *show* it to you, and hand you the means to build it yourself.

I had the *aha.* Now let me take you to the *cha-ching.*

And here's why I'm this confident: something big is happening. Agentic software is going through a paradigm shift. If that sounds grand, indulge me — I've written almost exactly those words before. Here's how I opened a blog post in April 2013, back at Juniper Networks, when the subject was network infrastructure management:

> *"This post is going to talk about managing networks in a whole new way. The concepts in it will change your life. They changed mine. There is no doubt that something big is happening. Our industry is going through a paradigm shift."*

I was right. I bet my career on that sentence and never looked back — and I didn't just *watch* that shift happen. I was part of a small, passionate core group of people who set out to help change the industry, and did. So when I tell you the same thing now, about agents, it isn't hype. It's pattern recognition from someone who has crossed this exact bridge once before — from a neighboring discipline into a field that wasn't ready for it.

So let me start with the assumption I think we're all quietly building on, and why it's broken: **that if we just write the instructions carefully enough, the machine will do as it's told.** It won't. It can't. **You cannot command an LLM — you can only elicit a promise and then verify it.** The teams who accept that *first*, who stop trying to command their agents and start doing something fundamentally different, are going to build the systems everyone else spends the next few years catching up to.

Here's the prize, concretely, so you know what I'm actually offering. One of the two example agents I'll show you — I call it **The Clinic** — takes *"I'm Ada Lovelace, book me a dermatology visit"* and turns it into a confirmed, eligibility-checked appointment, through real identity verification, a coverage check, and an actual scheduling API. And it **provably cannot** reach a state where it books before you're verified, or double-books a slot. Not because I asked it nicely in a prompt. Because the design makes those bad states *unreachable* — and I can prove it, exhaustively, before I ever deploy.

That *"and I can prove it"* is the whole game. It's the thing a prose prompt can never give you, and it's what the rest of this article is about. Let me tell you how I got there — starting, as these things do for me, with a paradigm shift I lived through once before.

## Part 1 — I've seen this before

Back in 2012 I was at Juniper Networks, deep in the Junos software world, when the head of networks at a Fortune 5 company asked me to make Puppet run on a switch. This was no idle question — a major sales deal hinged on the answer. My honest first reaction was, *"What is Puppet?"*

Then I looked, and the floor shifted under me. The sysadmins and the DevOps crowd had quietly gone through an entire revolution while the networking world wasn't paying attention. They'd stopped hand-configuring servers one at a time and started treating infrastructure as *code* — declarative, version-controlled, automatically enforced. The tools getting all the attention were **Puppet** and **Chef** — friendlier, wrapped in approachable languages that made the whole thing feel easy. But here's a detail whose weight I'd only feel years later: that entire declarative, desired-state model traced back to **CFEngine**, built in 1993 by a physicist named **Mark Burgess.** Puppet was essentially his idea, re-imagined to be easier to use. And while the newcomers took the spotlight, CFEngine was quietly running some of the largest deployments on earth — single installations north of a million machines. The foundational tool wasn't the famous one. Hold that name: it's the same Mark Burgess whose *Promise Theory* is the backbone of this article. His fingerprints were on the last paradigm shift I lived through, too — I just didn't know it yet.

And it was obvious, standing there, that the same wave was about to hit networking whether the networking industry was ready or not.

Part of why I could see it coming was where I stood: feet in two worlds. I reported into the Junos software team — learning from Phil Shafer, who essentially invented Junos automation — but my actual job was out in the field with the sales team, turning that engineering depth into closed deals. Engineer in one ear, customer in the other. Working across that boundary *was* the role — so much so that when I wrote the whole thing up in 2013, I called it "Bridging the Two Worlds." I've stood between worlds my whole career, which is probably why, years later, Mark's border-crossing ideas would feel like coming home.

I wasn't guessing, and I wasn't alone. At PuppetConf in 2013, John Willis — the mentor who gave me that "aha to cha-ching" phrase — pulled me aside and, in effect, handed me a crystal ball: *this* is what the next ten years of your career look like, he said, if you commit to the network-automation movement. I committed. And I had good company: Scott Robohn, my first manager at Juniper back in 2008, would go on to co-found the Network Automation Forum. I mention them because the point that matters for *this* article isn't that I *noticed* a paradigm shift — it's that I was in the room, often near the front of it, while one was made. I know what the early days of a real shift feel like from the inside. They feel like right now.

Here's the part of that story I want you to hold onto, because it turns out to be the whole point of *this* article. The vision was to run **Puppet** — the sysadmins' own automation — natively on the switch, so that when they rolled out an application, the network changes it needed rolled out *with* it: no ticket, no waiting on the networking team. And if the rollout went sideways, a single rollback reverted the application *and* the network together, as one unit. That was the truly game-changing part. The reason it actually *worked* — the reason the networking team could hand over that power without living in fear — came down to two ideas:

1. **Scoped authority.** Role-based access control that said, precisely, *who can do what.* Puppet didn't get the whole network. It got exactly the slice it needed.
2. **A guarantee underneath.** As I wrote back then, the networking team was comfortable handing over control because *"Junos can guarantee at the OS level that [Puppet] won't harm the network."*

Read those two ideas again with 2026 eyes. You give an autonomous actor **scoped authority** to act, and you put a **deterministic layer beneath it that guarantees it cannot cause harm — no matter what it tries.** You don't trust the actor. You trust the guarantee.

I've been designing systems around that principle for thirteen years. An LLM agent is just the newest, strangest, most capable actor I've ever been asked to hand the keys to. And when I started building agents, I promptly forgot my own hard-won lesson.

## Part 2 — The wall: I forgot my own lesson

Here's the kind of instruction I started out writing. I'd bet you've written one just like it:

> *"You are a helpful clinic assistant. Always verify the patient's identity before booking anything. Never book an appointment that isn't covered without confirming self-pay first. Never double-book a time slot."*

It reads beautifully. It sails through a design review. Everyone nods. And it is **impossible to verify.**

I learned that the way everyone learns it: in the logs. The agent booked an appointment before it verified who it was talking to. It offered a slot, the slot got taken, and it cheerfully booked a *different* time nobody asked for. Each time, I did the thing we all do — I went back to the prompt and added another sentence. *"Really, always verify first."* *"Do NOT book a different slot."* I was negotiating with it.

And one day it hit me that I was making the exact category mistake I'd spent a decade warning networking teams about. I was writing those instructions as if the words were *commands* the model would *execute.* But that's not what an LLM is. It's a stochastic sampler. On any given turn it can classify intent wrong, skip a step, or invent a tool argument. No wording fixes that, because the wording was never the problem. **A prompt is not a command. It's a request — a hopeful one.**

For a one-shot Q&A bot, who cares — a wrong turn is cheap and the next question resets everything. But for a **stateful, multi-step, safety-sensitive** agent, one that touches money or identity or anything you can't undo, that category mistake is the origin of every incident that keeps you up at night. Because it leaves the one question you actually need answered completely unanswerable:

> *Can this agent ever reach a state it must never be in?*

With a prose prompt, the most honest answer I could give was: *"Probably not. But I can't prove it."*

I hate that answer. It's the "oh crap, is it the network?" of agent design — the sinking feeling that something's wrong and you have no way to know whether your own system is the cause. I'd forgotten what made 2013 work: you don't make the actor trustworthy by asking nicely. You put a guarantee underneath it. So I went looking for the agentic version of that guarantee.

## Part 3 — The reframe: an LLM is an autonomous agent

What unstuck me wasn't an AI paper. It was a body of work called [**Promise Theory**](http://markburgess.org/promises.html), developed by [Mark Burgess](http://markburgess.org/) and formalized with Jan Bergstra. It's about two decades old, and — this is not a coincidence — it comes from the very same configuration-management and distributed-systems world that gave us Puppet and Infrastructure as Code in the first place. The neighboring discipline came to my rescue twice in one career — and both times, it turned out, through the same man's ideas.

Here's something worth sitting with before we go further. Burgess spent the better part of twenty years developing Promise Theory, and for most of that time it lived at the margins — precisely *because* it refuses to stay inside one discipline. It draws on physics, on logic, on distributed systems, on the plain study of how autonomous things cooperate. Ideas that travel across borders like that are the easiest for any single field to wave off as "not our department" — and they are also the ones that, when someone finally listens, turn out to explain the thing nobody else can. Promise Theory was built to reason about autonomous agents more than a decade before the most important autonomous agent any of us would ever build — the LLM — even existed. It was *right,* and it was *early,* and it was *waiting.* I'm listening now. I think you should too.

Promise Theory reasons about systems built from **autonomous** parts, and its founding axiom is deceptively simple:

> An agent is autonomous. It can only make promises about *its own* behavior. No other agent can impose a promise upon it.

You cannot *force* another agent to do anything. You can only ask — and it decides. Promise Theory gives that ask a name: an **imposition.** A command, a hint, a request — all impositions, and all of them guarantee exactly nothing, because the target is autonomous. The only thing an agent can genuinely give you is a **promise:** a declaration about *itself* that you, the recipient, can then rely on and — here's the load-bearing word — **assess.**

Now read that axiom again with an LLM in mind, because this is where I sat up straight:

**Everything Promise Theory says about autonomous agents is true of an LLM as a matter of engineering fact — not as a metaphor.**

- You cannot impose behavior on it. No prompt *guarantees* an action.
- The most a prompt can do is *elicit a promise* to behave a certain way. Because the promiser is stochastic, you the recipient **must** verify.
- It is one autonomous agent among several — the model, the code around it, the external APIs, the human. There is no privileged commander in the room.

That's the reframe, and it changed how I build. Teams that treat prompts as commands spend their lives asking "why won't it obey?" Teams that treat prompts as **promises requiring assessment** build the guarantee on day one. I'd been living in the first camp, having forgotten I already knew how to live in the second.

If you take one idea from this article, take this one: **you can't command an LLM. You can only elicit a promise and then assess whether it was kept.** I've started calling the whole approach that follows from it **promise-and-assess** — and it is the direct descendant of "hand over scoped authority, guarantee no harm underneath." Everything that follows is me making that phrase concrete enough to build on.

## Part 4 — The gap nobody talks about

Here's where most write-ups about Promise Theory and AI stop. They land the beautiful reframe, quote the axioms, leave you nodding — and give you absolutely no idea what to do Monday morning.

That gap gnawed at me. Promise Theory is, frankly, PhD-level material — formal definitions, polarities, a whole algebra of conditional promises. The reframe is genuinely clarifying. But "treat your LLM as an autonomous promiser" is not something I can hand an engineer and say "go build it." Where does the promise *live?* What file is it in? How do I check it? How does it survive contact with a real framework and a real deploy?

That's the question this whole piece is really about: **how do you get from a profound idea to something you can actually run?** In 2013 the answer was a Puppet agent cross-compiled onto Junos. This time I had to build the bridge myself. I ended up shipping it as an open-source kit with two complete, runnable example agents. Let me show you the bridge. There are only a handful of moving parts, and none of them are exotic.

## Part 5 — The bridge: one artifact, three readers

Here's the move that made everything click. Instead of a prose prompt, each agent's *entire* instruction set becomes a single document — I call it a **contract.** And the trick is that this one document is read by three different consumers, each taking what it needs:

1. a **model checker,** which proves the agent can never reach a bad state,
2. the **code that builds the agent,** which reads its declared promises, and
3. the **LLM itself,** which reads the whole thing as its operating instructions.

One artifact. Three readers. Same bytes. That last part matters more than it sounds, and I'll come back to it.

At the center of the contract is a small **state machine,** written in a language called [FizzBee](https://fizzbee.io) — it's in the TLA+ family of formal specification languages, but with a Python-ish syntax that reads approachably. Here's the actual rule from **The Clinic** — the clinic-appointment assistant that's one of two runnable example agents in the kit — verbatim:

```fizz
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

Now the payoff. A **model checker** takes that machine and explores *every reachable combination of states* the actions can produce, and confirms no invariant is ever broken. I run it offline, in CI, before anything ships:

```
[PASS] book_appointment
[PASS] clinic_orchestrator
[PASS] manage_appointment
3/3 contract(s) passed model checking.
```

Remember my unanswerable question — *"can it ever reach a bad state?"* This answers it. Not with "probably not." With **"no, and here's the exhaustive proof."** This is the 2013 guarantee, grown up: back then Junos guaranteed at the OS level that Puppet couldn't harm the network; here the model checker guarantees, at design time, that the agent can't reach a state it must never be in.

And this is not a toy that only passes because I wrote it to pass. My second example is the Trials of the Holy Grail — yes, the Monty Python one, knights and the Bridge of Death and the Knights Who Say "Ni!" — with a Quest Marshal that should grant the Grail quest only after *both* trials are passed. **Its first draft failed model-checking.** The checker found a sequence I never would have: a knight could re-attempt a trial he'd already passed, fail it *after* the Grail was granted, and blow the invariant. The tool handed me the exact step-by-step trace to the bad state. The fix — make a passed trial "sticky" — took two minutes. That's a real bug, caught by exhaustive search, before any human or any model ever touched the agent. Prose could never have caught it.

Now, "same bytes." In the usual setup — a state machine coded in one place, a prompt written in another — the machine and the instructions are *two different artifacts that drift.* You fix one, forget the other, and find out in production. Here, the state machine the checker proves and the instructions the model reads are **the same document.** They can't drift, because there's nothing to drift from.

## Part 6 — Formalize the structure, leave judgment to prose

I am *not* telling you to formalize your whole agent. That way lies madness. The single most useful rule I found is about where to draw the line:

> **Formalize structure and ordering. Leave judgment and phrasing to prose.**

"Verify before you book," "never double-book," "at most one task suspended at a time" — those are structural. They're about ordering and safety, and they belong in the model-checked state machine, because prose lets them drift.

But "is this message a greeting or a booking request?" is not a formal property and never will be. Neither is "how do I phrase this hand-off warmly?" That's judgment. It stays in prose — in a section of the contract I call step-guidance — right beside the formal parts but clearly quarantined from them.

Don't try to formalize the fuzzy stuff; you'll fail and hate your life. Don't leave the structural stuff to prose; it'll drift and hurt you. Getting that line right is most of the skill.

## Part 7 — The part you cannot skip

Now the biggest caveat, because it's the thing that separates a real contract from theater — and it's the same lesson from 2013, dressed in new clothes.

**Model-checking proves the specification. It does not prove the LLM follows the specification.**

The proof certifies that the *state machine* can't reach a bad state. It says nothing about whether your stochastic model actually stays on the legal path. The model can still misread eligibility, skip a guard, or fabricate an argument. If you model-check your contract, ship it as a prompt, and stop there, you've bought false confidence — which is worse than none.

Promise Theory explains why in one line: *a promise from an unreliable promiser is worthless to you without independent assessment.* And this is exactly what "Junos guarantees at the OS level" was doing all along — it never trusted the automation reaching in to make changes; it enforced the boundary underneath, no matter what that automation tried. So every safety invariant gets a twin. Take the no-double-book rule:

```fizz
always assertion NoDoubleBook:
    return (not appointment_booked) or slot_available
```

That invariant is the LLM's *promise:* "I'll never book a taken slot." The **assessment** is real code — the scheduling service itself refuses to commit a slot that isn't open, no matter what the model says. The model can promise all day; the code is what decides whether the promise was kept, and quietly refuses when it wasn't.

This LLM-promise-plus-code-assessment pair is, to me, the atomic unit of the whole method. **Never a stochastic promise standing alone. Always a stochastic promise backed by a deterministic guarantee.** The model check proves the map is coherent; the code polices the territory. You need both, and the code half is not optional. It is the 2026 version of "guarantee at the OS level that it can't harm the network."

## Part 8 — From one agent to a system of agents

Everything so far makes a *single* agent trustworthy. But The Clinic isn't one agent — it's a small society of them behind one friendly face: an orchestrator that verifies you and routes your request, a booking subagent, a subagent that cancels and reschedules, plus non-LLM service agents for the schedule, the insurance check, and the patient registry.

Draw a boundary around that whole society and treat it as one agent making a single promise to the patient — *"I'll book your appointment"* — and you have what Promise Theory calls a **superagent**: one face to the outside, a promise graph within. Mark Burgess's rule is that *"we may choose the boundary of an agent wherever we please,"* and that freedom is the point. The patient talks to one agent; inside, it's a society.

This is where I think Promise Theory earns its keep most, because multi-agent systems rot in the same place every time: **hidden dependencies.** One agent writes some shared state, another silently reads it, and nobody declared the handoff. It works until it doesn't. (Networking people: this is the "pinprick of death" all over again — a thousand tiny uncoordinated changes.)

Promise Theory drags every one of those dependencies into the open using two polarities. An agent makes an **offer** (`+`) — "I will provide this" — or a **use** (`−`) — "I will accept and use that." Both are promises; the `−` is not mere dependence, it's an agent promising to accept what another offers. And the rule that does the work: cooperation only *binds* when a `+` offer meets a matching `−` use. An offer nobody uses, or a use nothing offers, is a **design defect you can detect mechanically.**

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

**The orchestrator owns nothing.** This one took me a while to fit my brain. Under the autonomy axiom, the orchestrator *cannot* promise that a subagent will book anything — it can only promise *its own* behavior: verify the patient, classify intent, relay to the subagent whose offer matches, remember at most one suspended task, relay the result. Routing stops being a *command* and becomes **selection among published offers.** The orchestrator never reaches inside a subagent to make it act; it uses the subagent's conditional offer, and the subagent's own guards are the real gate. If the subagent refuses, the orchestrator relays the refusal — it doesn't override it. (That's RBAC thinking — "who can do what" — grown into a full graph.)

**Shared state becomes an agent.** Instead of a blackboard the orchestrator scribbles on and the subagents peek at, the patient registry is its *own* agent that publishes the verified patient; consumers declare that they rely on it. The invisible dependency becomes a declared, checkable binding — impossible to forget when you add a third workflow six months later.

**The whole graph is verified offline.** Just as the state machines get model-checked, the promise manifests get checked for completeness: every `−` use meets a `+` offer, and every condition is either met by some agent's offer or explicitly self-assessed. An agent relying on something nobody promised is a **build failure, not a 2 a.m. surprise.**

So the wager scales. For one agent it was *"can this reach a bad state?"* For the superagent it becomes *"can this society of agents make a promise it has no way to keep?"* — and I answer that before I deploy, too.

I believe the engineers building serious systems must have **choice and control** — choice of tools, frameworks, and languages, and control over how they build, deploy, and evolve. Any method worth adopting has to honor that instead of locking you in. So the property I care about most here isn't a feature at all; it's that the method asks nothing of your stack. The two examples prove it: The Clinic and the Trials of the Holy Grail run on **entirely different frameworks** — The Clinic on Google's ADK, the Trials on Pydantic AI — yet they share the *same* contracts and the *same* enforcement code. The only meaningful difference between them is a single file wiring each to its runtime. Everything that makes them *safe* is identical and framework-independent. The method lives in the contracts and the assessment code — not in anybody's framework-of-the-month. Choose your tools; keep your guarantees.

## Part 9 — What you actually walk away with

I don't want to leave you with a vibe. Here's the distilled standard I now hold my own agents to. If you build nothing else from this article, run your current design past these:

1. **Treat every model as an autonomous agent.** Design for elicited promises and mandatory assessment, not compliance. This ends the "why won't it obey?" spiral, because you stop expecting obedience.
2. **Make each agent's self-promises a model-checked contract.** Formalize ordering and safety as a state machine; prove it exhaustively offline. Keep judgment in prose, quarantined so it can't corrupt the guarantees.
3. **Every condition names who satisfies it.** No hidden dependencies. A condition is either self-assessed or met by a named agent's offer.
4. **Pair every stochastic promise with a deterministic guarantee.** The enforcement code isn't belt-and-suspenders. It's the whole point. Never ship the contract without it.
5. **Declare what you rely on; forbid unmatched edges.** Every use meets an offer. Relying on something nobody promised is a build failure.
6. **Derive the outside promise from the inside.** A superagent — a society of agents behind one face — must generate what it advertises to the world from what its members actually offer, so it can never overstate what it delivers.

Points 1–2 make a single agent trustworthy — that's where most teams stop, if they get there at all. Points 3–6 make a *system* trustworthy. And I genuinely believe this is where agentic engineering is heading, whether or not anyone uses the word "promise," because the premise underneath it is simply *true:* the model is an autonomous stochastic agent, and autonomous agents can only be promised, then assessed.

## Part 10 — When *not* to do this

I'd be doing you a disservice if I pretended this is free. It isn't, and knowing where it *doesn't* pay off is part of using it well.

A formal contract is more work than a paragraph. It costs tokens every turn, because it rides in the context window. It asks your team to read a state machine and run a model checker in CI. And — I'll say it a third time, because it's the trap — the model check proves the spec, not the behavior, so the enforcement code is mandatory, which is *more* engineering, not less.

So **skip it** for one-shot Q&A, a single-tool lookup, or a throwaway prototype where a wrong turn costs nothing. There, a good prose prompt is exactly the right tool and a contract is just ceremony.

**Reach for it** when you've got multi-step workflows, ordering or safety constraints that truly must hold, actions involving money or identity or anything irreversible, and a system you need to evolve without quietly regressing. That's precisely the situation where "probably not, but I can't prove it" isn't good enough — and it's the situation I keep finding myself in.

## Part 11 — Looking back over the bridge

We opened on a paradigm shift and a bet. Between there and here we've walked the whole method: the wall of the prose prompt, the reframe that an LLM is an autonomous agent, the contract three readers share, the model check that proves the bad states unreachable, the enforcement code that keeps the promise against a stochastic promiser, and the promise graph that scales it all up to a superagent.

Strip away the machinery and one shape remains — and it's the same shape from 2013. An autonomous actor, handed scoped authority, made safe not by trust but by a guarantee underneath. Then the actor was a config-management agent and the guarantee lived in the OS. Now the actor is an LLM and the guarantee lives in a model-checked contract and its enforcement code. Same idea. New actor. That's the whole reason I'm confident this is a real shift and not a fashion: I've watched this exact pattern cross a boundary from a neighboring discipline once already, and I've spent thirteen years living inside the field it remade.

The prize I promised you at the very top — The Clinic that *provably cannot* book before you're verified — isn't a trick of a clever prompt. It's the payoff of that shape, made concrete: the contract makes the bad states unreachable, the code makes every promise assessed, and the promise graph makes every dependency something we declared out loud.

I packaged the whole thing as an open-source kit: the two runnable examples, the schemas, a project template that scaffolds a new contract-driven agent that's green out of the box, and an authoring skill that walks you through writing your first contract. You can model-check the examples *and talk to them.*

So here's my ask, the same one I made in 2013: go try it. Take a small, stateful agent you already have — one where a wrong turn actually costs something — and write its rules as a contract instead of a prompt. Run the model checker. Watch it find the state you didn't think of. Then come tell me what it caught.

You can't command an LLM. But you can get a promise out of it, and you can guarantee the rest. I've bet on this shape before. I'm betting on it again — and this time, I'd love for you to build it with me.

---

*The [promise-driven-agentic-kit](#) is open source under Apache-2.0. Start with the whitepaper, then open The Clinic example. Corrections and extensions welcome — this is a living kit, and I mean that.*

*With deep gratitude to Mark Burgess, whose Promise Theory is the foundation everything here is built on. If this article did its job, don't stop at it — go to the source: his* [Book of Promises](http://markburgess.org/BookOfPromises.pdf) *(the full* Promise Theory: Principles and Applications*, with Jan Bergstra, free to read online), the more approachable* Thinking in Promises *(O'Reilly), and his [essays and writing](http://markburgess.org/). Thanks, too, to the FizzBee project for the model checker that makes the proofs run.*

*I've not yet had the pleasure of meeting Mark; by the time these words find their proper audience, I hope that's changed.*
