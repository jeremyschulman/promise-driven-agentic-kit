# Promises, Promises — Why Do I Believe?

### Twenty years ago Mark Burgess forged the foundations of the DevOps Era. His Promise Theory is poised to do the same for the Agentic Era.

*By Jeremy Schulman · Part 1 of 3*

---

**TL;DR:** if you just want to look at a GitHub repo: `<Github repo: TBD>`.

Does this sound like you?

> *As a software engineer evolving our business-process automation into the era of AI, I need to build systems where many AI agents work together to carry out complex, multi-step workflows, reliably enough to run the business on.*

If so, I promise to blow your mind. I know how that lands. You have no reason yet to
believe me. Good. *Trust, but verify.* Hold onto that instinct; it's the whole
point, and we'll get there.

I've recently had an "Ah, Ha!" moment that I want to share with you. Across
three articles I want to take you all the way from the "Ah, Ha!" to the "Cha,
Ching!"; to the point where you can put into practice what you are going to read
about. This is not about another shiny demo or agentic development framework. I
want to share with you an entirely different _approach_ to building
sophisticated agentic solutions.

And a confession before we start: I came to agentic AI recently, at the start of 2025, as new
to it as you may be — and afraid of the same thing everyone is. What if the
agent goes rogue and takes down something I can't afford to lose? We'll come
back to that fear; where it went is part of the story.

Let's get going! This first piece makes the case. The two that follow show you the way, starting with [Everybody Wants to Rule the World — How to Build an Agent with Provable Boundaries](medium-part-2-everybody-wants-to-rule-the-world.md)
and wrapping up with [Games Without Frontiers — How to Check a System's Declared Promise Graph](medium-part-3-games-without-frontiers.md).

## Mr. Roboto

For almost two years I've been building and running in production something the
enterprise world has long, and frankly boringly, called **business process
automation**, or BPA. In the Era of AI, I am creating *autonomous* BPA. These
solutions act on their own, end to end, inside limits I can prove. Stateful,
multi-step, safety-sensitive systems that carry real organizational work. While
much of what you read about AI talks about copilots, chatbots, coding
assistants, and other such personal-productivity tools, I've been automating the
boring stuff, and building it in a completely different way.

My "customers" are the business units I serve. They want **outcomes** regardless
of whether AI is used on the inside. Executives want to understand whether the
money going into AI is showing up as material business value. Autonomous BPA
speaks to both: it delivers the effect of *added staff*, value at the level of
the whole organization. Before AI, the sheer complexity of these use-cases kept
them off the table. The workflows were too tangled, too full of institutional
knowledge, to automate the old way. In 2025, for me at least, AI became the
enabling technology that finally made them possible.

Along the way I worked out a technique for building them that I haven't seen
anywhere else. So I'm not talking hypotheticals. I'm going to *show* it to you,
and provide you the means to try this out for yourself.

So let me start with the assumption I think we're all quietly building on, and
why it's broken: **that if we just write the instructions carefully enough, the
machine will do as it's told.** It won't. It can't. **You cannot command an LLM.
You can only elicit a promise and then verify it.** And the teams who accept that *first* — who stop trying to command their agents and start doing something fundamentally different — are going to build the systems everyone else spends the next few years catching up to.

One of the two example agents I'll show you (in the Github repo), which I call
**The Clinic**, takes an input *"I'm Ada Lovelace, book me a dermatology visit"*
and turns it into a confirmed, eligibility-checked appointment, through real
identity verification, a coverage check, and an actual scheduling API. Its specified
model makes booking before verification and double-booking unreachable, and its
authority services independently refuse those operations at runtime. Not because I
asked it nicely in a prompt. Because the design claim is checked exhaustively before I
build, and the controlled state is guarded when the system runs.

That *"and I can prove it"* is the whole game. It's the thing a prose prompt can
never give you. And make no mistake, something big is happening: agentic
software is going through a paradigm shift. Let me tell you how I got here.

## I've Been Here Before

Let me try an opening on you: *This post is going to talk about building agentic
systems in a whole new way. The concepts in it will change your life. They
changed mine.*

I've said almost exactly those words before. Here's how I opened a blog post in
April 2013, back at Juniper Networks, when the subject was network
infrastructure management:

> *"This post is going to talk about managing networks in a whole new way. The
> concepts in it will change your life. They changed mine. There is no doubt that
> something big is happening. Our industry is going through a paradigm shift."*

I was right. I bet my career on that sentence and never looked back, and I
didn't just *watch* that shift happen. I was part of a passionate group of
people around the world who set out to help change the industry, and did. So
when I tell you the same thing now, about agentic engineering, it isn't hype.
It's pattern recognition from someone who has crossed this exact bridge once
before: from a neighboring discipline into a field that wasn't ready for it.

Back in 2012 I was at Juniper Networks, deep in the Junos software world, when
the head of networks at a Fortune 5 company asked me to make Puppet run on a
switch. This was no idle question; a major sales deal hinged on the answer. My
honest first reaction was, *"What is Puppet?"*

Then I looked, and the floor shifted under me. The sysadmins and the DevOps
crowd had quietly gone through an entire revolution while the networking world
wasn't paying attention. They'd stopped hand-configuring servers one at a time
and started treating infrastructure as *code*: declarative, version-controlled,
automatically enforced. The tools getting all the attention were **Puppet** and
**Chef**, friendlier, wrapped in approachable languages that made the whole
thing feel easy. But here's a detail whose weight I'd only feel years later:
that entire declarative, desired-state model traced back to **CFEngine**, built
in 1993 by a physicist named **Mark Burgess.** Puppet was a friendlier take on
the paradigm he pioneered. And while the newcomers took the spotlight, CFEngine
was quietly running some of the largest deployments on earth, single
installations north of a million machines. The foundational tool wasn't the
famous one. Hold that name: it's the same Mark Burgess whose *Promise Theory* is
the backbone of this article. His fingerprints were on the last paradigm shift I
lived through, too. I just didn't know it yet.

And it was obvious, standing there, that the same wave was about to hit
networking whether the networking industry was ready or not.

Part of why I could see it coming was my unique role. I had my feet in two
worlds. I reported into the Junos engineering software team. My real job was
out in the field with the sales team, using my deep knowledge of Junos
automation to help sell the value of Junos. I found I have this weird
split-brain: software engineering and business go-to-market. Working across that
boundary *was* the role. So much so that when I wrote the whole thing up in 2013,
I called it "Bridging the Two Worlds." I've stood between worlds my whole
career, which is probably why, years later, Mark's border-crossing ideas would
feel like coming home.

## The Future's So Bright, I Gotta Wear Shades

At PuppetConf in 2013, I gave a talk on running Puppet natively on Junos switches. Afterward John Willis — a leader of the DevOps movement — came up, genuinely excited about it. That's how we met, and how he became a mentor: the one who gave me the "Ah, Ha!" to "Cha, Ching!" phrase. He pulled me aside and, in effect, handed me a crystal ball: *this* is what the next ten years of your career look like, if you commit to the network-automation movement. I committed.

And I had good company: Scott Robohn, my first manager at Juniper back in 2008, would go on to co-found
the Network Automation Forum. My friend Peter Sprygada and I co-wrote the Puppet
"netdev" module together; Peter went on to become the driving force behind
Ansible's network automation, the reason so much of the world's network
infrastructure is automated the way it is today. I mention them because the
point that matters for *this* article isn't that I *noticed* a paradigm shift.
I was in the room, often near the front of it, helping to make the shift happen. I
know what the early days of a real shift feel like from the inside.

And I've got that _funny feeling_ again, right now.

## Catch Me I'm Falling

There's a team-building ritual where you close your eyes, cross your arms, and drop straight backward — trusting the people behind you to catch you. A promise to catch, and pure faith they'll keep it. I don't take that bet with complex systems. I do the version where I ensure there's a net. Everything I learned in 2013 was about building that net.

Here's a key insight from the Puppet story I want you to hold onto, because it
turns out to be the whole point of *this* article. The motivation was to run Puppet, the sysadmins' own automation tool, natively on the switch: when they rolled out an application, the network changes it needed rolled out *with* it — no ticket, no waiting on the networking team. And if the rollout went
sideways, a single rollback reverted the application *and* the network together,
as one unit. That was the truly game-changing part for the customer. The reason
this radical approach worked, the reason the networking team could hand over
that power without living in fear, and the key insight learned, came down to two
ideas:

1. **Scoped authority.** Role-based access control that said, precisely, *who can do what.* Puppet didn't get the whole network. It got exactly the slice it needed.
2. **A guarantee underneath.** As I wrote back then, the networking team was comfortable handing over control because *"Junos can guarantee at the OS level that [Puppet] won't harm the network."*

Read those two ideas again with 2026 eyes. You give an autonomous actor **scoped
authority** to act, and you put a **deterministic layer beneath it that
guarantees it cannot cause harm, no matter what it tries.** You don't trust the
actor. You trust the guarantee.

In 2014 I left Juniper to chase the idea further, and joined the startup that
became Apstra, which pioneered *intent-based networking.* The thesis was
simple, and to me revelatory: start with a single declarative **intent**, a
description of what the network should *be* that you can programmatically reason
about. From that one intent you derive two things: (1) the configuration that
drives the network into that state, *and* (2) the tests that continuously
validate it stays there. Change the intent, and both flow from it in lockstep.
Nothing drifts, because there is one source of truth and everything else is
derived from it. I carried that philosophy when I presented at the Network
Automation Forum's inaugural event (the forum Scott Robohn helped found) in a
talk I called *Design Driven Network Assurance.* That pattern is in my DNA.

I've spent more than a decade designing around two hard-won instincts: (1) start
from a single declarative source of truth, and (2) put deterministic guarantees
underneath the actor. An LLM agent is just the newest, strangest, most capable
actor I've ever been asked to hand the keys to, and when I turned to building
agents I gravitated toward that same shape. It *felt* right. But I'm a
practitioner, not a theorist. Feeling right isn't the same as knowing, and the
only way to know is to build it and watch what happens. I started building.

## Fumble Around and Find Out

Here's the kind of instruction I started out writing. I'd bet you've written one just like it:

> *"You are a helpful clinic assistant. Always verify the patient's identity before booking anything. Never book an appointment that isn't covered without confirming self-pay first. Never double-book a time slot."*

It reads beautifully. It sails through a design review. Everyone nods. And it is **impossible to verify.**

I learned that the way everyone learns it: in the logs. The agent booked an
appointment before it verified who it was talking to. It offered a slot, the
slot got taken, and it cheerfully booked a *different* time nobody asked for.
Each time, I did the thing we all do: I went back to the prompt and added
another sentence. *"Really, always verify first."* *"Do NOT book a different
slot."* I was negotiating with it.

And one day it hit me that I was making the exact category mistake I'd spent a
decade warning networking teams about. I was writing those instructions as if
the words were *commands* the model would *execute.* But that's not what an LLM
is. It's a stochastic sampler. On any given turn it can classify intent wrong,
skip a step, or invent a tool argument. No wording fixes that, because the
wording was never the problem. **A prompt is not a command. It's a request, a
hopeful one.**

For a one-shot Q&A bot, who cares: a wrong turn is cheap and the next question
resets everything. But for a **stateful, multi-step, safety-sensitive** agent,
one that touches money or identity or anything you can't undo, that category
mistake is the origin of every incident that keeps you up at night. Because it
leaves the one question you actually need answered completely unanswerable:

> *Can this agent ever reach a state it must never be in?*

With a prose prompt, the most honest answer I could give was: *"Probably not. But I can't prove it."*

That didn't work for me. It's the "oh crap, is it the network?" of agent design:
the sinking feeling that something's wrong and you have no way to know whether
your own system is the cause. I'd forgotten what made 2013 work: you don't make
the actor trustworthy by asking nicely. You put a guarantee underneath it. So I
went looking for the agentic version of that guarantee.

## A Kind of Magic

I'm a practitioner. I like to live at the intersection of emerging technology and
business acceleration, which means I rarely start from theory. I start by trying
things and keeping what works.

So in 2025 I experimented. If prose was too loose, maybe structure would tighten
it. I moved my instructions into YAML, betting that a data format would rein the
model in. It helped a little, but the style was still *imperative*: I was
writing the same step-by-step commands, just in tidier brackets, and the
hallucinations kept coming. I was still trying to command the thing.

Then I read about POML, Microsoft's Prompt Orchestration Markup Language, which
encodes prompts as XML. I didn't agree with the specifics of their approach, but
it lit a fuse. What if I used XML not to organize *commands*, but to declare
*intent*: goal-oriented, with tags and attributes that carried real semantic
meaning? Instead of telling the model *how* to act, step by step, I would
declare *what* a correct outcome looked like and let it find the path.

That change did something I didn't expect. It wasn't only that the agent worked
more often. It was that the *failures changed shape.* Instead of writing a mess
of defensive code to catch unpredictable output, I found that when the model did
fail, it failed in specific, legible ways I could guardrail cleanly. The
structure made the failures tractable. So I dropped prose entirely and went to
XML, writ large.

But I still couldn't be *absolutely sure* about anything. I had better odds, not a
guarantee, and 2013 had already taught me that better odds are not the same as a
promise you can keep.

## A Serendipitous Conversation

The next piece fell into place in 2026, and it was pure luck. I was at a
conference where John Willis was speaking. I had an engaging conversation with
an associate professor from Brown University. He was presenting on *formal
methods*: the mathematics of proving that a system can never misbehave. I asked
him a question that started to nag at me. *Could you write an agent's
instructions in the symbolic language of formal methods?* It is so concise, so
exact, maybe, perhaps, an LLM would be more effective using that form of
language. We talked, and I left with more questions than answers, but with a
strong sense that there was *something there.*

I went looking at formal method languages and found [FizzBee](https://fizzbee.io).
I had braced for TLA+, the venerable formal-methods language from Leslie Lamport (the same computer scientist who gave us LaTeX, and it reads that way).
FizzBee was different. It looked and read like Python. And as I worked through
its concepts, something clicked. *I think this feels like Promise
Theory.* I was only passingly familiar with Promise Theory at that point, but I knew
enough to feel the resonance. So I went to learn more.

## Finding a Shared Language

What I found validated my feelings. By the time I started reading up on [**Promise Theory**](http://markburgess.org/promises.html) — developed by [Mark Burgess](http://markburgess.org/) and formalized with Jan Bergstra — my XML + FizzBee experiment was already working. That's exactly why it hit so hard: here was a proven, decades-old body of theory describing, in precise terms, the very thing I'd stumbled into by feel.

But the part I cared about most was language. Everything I build, I want to express in one shared language — because the fewer private vocabularies a system carries, the less cognitive load and operational friction it puts on everyone and everything that touches it: the engineers, the LLM, the tools. Coining my own framework or DSL does the opposite; it's one more language the whole team, and the model, has to learn.

So rather than invent terms, I put Promise Theory's vocabulary *in the code* — agents, promises, offers, and uses, named the way Burgess names them. When an engineer opens a contract, they meet established terms, not jargon I made up; when a tool renders a diagram from it, it speaks the same vocabulary. People and tools end up sharing one mental model. And because Promise Theory is proven and decades old, I wasn't inventing that language, I was standing on it. Puppet and Chef stood on the shoulders of giants; Mark was one of them. The proofs make the design *provable*; the shared language keeps the whole thing *legible*.

And this matters more now than it would have a few years ago. A DSL was always a shortcut *for humans* — Puppet and Chef built their languages so an engineer hand-crafting a manifest or a recipe had less to remember. But I'm not hand-crafting anymore; an AI coding assistant writes most of this with me, and it already speaks XML and XSD fluently, with terms plain enough — agents, promises, offers, uses — that it isn't flying blind. Invent a brand-new DSL and I'd be handing the model a language it has never seen, defeating the very thing that makes AI-assisted development work. So I did the opposite: the contract is plain XML, its structure pinned by an XSD — not a new grammar, just a shape the model has read a million times. I hand it the schema; it writes fluent, correct contracts back. Reusing what the model already knows isn't a compromise. It's the point.

## An LLM Is an Autonomous Agent

Here's something worth sitting with before we go further. Burgess spent the
better part of twenty years developing Promise Theory, and for most of that time
it lived at the margins, precisely *because* it refuses to stay inside one
discipline. It draws on physics, on logic, on distributed systems, on the plain
study of how autonomous things cooperate. Ideas that travel across borders like
that are the easiest for any single field to wave off as "not our department."
They're also the ones that, when someone finally listens, turn out to explain
the thing nobody else can. Promise Theory was built to reason about autonomous
agents more than a decade before the most important autonomous agent any of us
would ever build (the LLM) even existed. It was *right,* and it was *early,* and
it was *waiting.* I'm listening now. I think you should too.

Promise Theory reasons about systems built from **autonomous** parts, and its founding axiom is deceptively simple:

> An agent is autonomous. It can only make promises about *its own* behavior. No other agent can impose a promise upon it.

You cannot *force* another agent to do anything. You can only ask, and it decides. Promise Theory gives that ask a name: an **imposition.** A command, a hint, a request: all impositions, and all of them guarantee exactly nothing, because the target is autonomous. The only thing an agent can genuinely give you is a **promise:** a declaration about *itself* that you, the recipient, can then rely on and (here's the load-bearing word) **assess.**

Now read that axiom again with an LLM in mind, because this is where my brain started to hyperventilate:

**Promise Theory's autonomy lens exposes engineering facts that an LLM-based system
cannot wish away.**

- You cannot impose behavior on it. No prompt *guarantees* an action.
- The most a prompt can do is *elicit a promise* to behave a certain way. Because the promiser is stochastic, you the recipient **must** verify.
- It is one autonomous agent among several: the model, the code around it, the external APIs, the human. There is no privileged commander in the room.

*Oh my god,* I kept thinking, *this is the way.* And then again. And again.

That's the reframe, and it changed how I build. Teams that treat prompts as commands spend their lives asking "why won't it obey?" Teams that treat prompts as **promises requiring assessment** build the guarantee on day one. I'd been living in the first camp, having forgotten I already knew how to live in the second.

If you take one idea from this article, take this one: **you can't command an LLM. You can only elicit a promise and then assess whether it was kept.** I've started calling the whole approach that follows from it **promise-and-assess.** It's the direct descendant of "hand over scoped authority, guarantee no harm underneath."

## She Blinded Me with Science

Then the "Ah, Ha!" struck like lightning: three ideas I'd been circling separately snapped into one. Declarative XML made an agent's intent legible — to me, to the model, and to a checker. A formal-methods language could *prove* a design never reaches a bad state. And Promise Theory was the connective tissue: a shared language, understood by people and tools alike, that let me compose many agents into one system. Gunpowder is three inert ingredients that do nothing apart and level a wall together. This was that. The XML became a *contract.* Formal methods made it *provable.* Promise Theory made it *composable.*

But a spark isn't a running system. And this is where most write-ups about
Promise Theory and AI stop: they land the reframe, quote the axioms, and leave
you nodding, with no idea what to do Monday morning. That gap is exactly where
the real work lives. "Treat your LLM as an autonomous promiser" is a beautiful
idea and completely inert until you can answer: where does the promise *live?*
What file is it in? How do you check it? How does it survive contact with a real
framework and a real deploy?

So I put together what I'm calling the **promise-driven-agentic-kit**: a set of files that help a software engineer turn these ideas into a real agentic solution, in Python. You don't so much *run* it as *build* with it. The companion to this piece, **[Everybody Wants to Rule the World — How to Build an Agent with Provable Boundaries](medium-part-2-everybody-wants-to-rule-the-world.md)**, walks the whole method: the single contract document that a model checker, your build code, and the LLM all read from; the state model that makes booking before verification unreachable under its assumptions; and the authority code that assesses proposals while keeping its own safety promise.

## Here I Go Again

That fear from the start — the rogue agent, the blast radius — here's where it went. A year ago I meant to hand-write every line myself, using AI assist only in small, supervised doses. Today I let an AI coding assistant write essentially all of it, because a model-checked contract and independently tested authority boundaries make the risk bounded and inspectable. If the arc feels familiar, it should: it's the same one I watched a generation of network engineers walk — "you'll get the CLI out of my cold, dead hands" in one breath, "okay, fine, automate it" a decade later. Fear turns to trust the moment a guarantee shows up underneath. That's the real journey — mine, theirs, and maybe now yours.

For now, hold onto the instinct I asked you to keep at the very top. Why should you believe an LLM's promise? You shouldn't, not on its own. You elicit the promise, and then you verify it. *Trust, but verify.* Here, that isn't a proverb. It's the whole method, and it's buildable. Let me prove it to you.

---

*With deep gratitude to Mark Burgess, whose Promise Theory is the foundation everything here is built on. If this piece did its job, go to the source: his* [Book of Promises](http://markburgess.org/BookOfPromises.pdf) *(the full* Promise Theory: Principles and Applications*, with Jan Bergstra, free to read online), and the more approachable* Thinking in Promises *(O'Reilly).*

*I've not yet had the pleasure of meeting Mark; by the time these words find their proper audience, I hope that's changed.*

---

*Liner notes: this piece takes its name from "Promises, Promises" (Naked Eyes, 1983), and its section titles nod to "Mr. Roboto" (Styx, 1983), "The Future's So Bright, I Gotta Wear Shades" (Timbuk3, 1986), "Catch Me I'm Falling" (Pretty Poison, 1987), "A Kind of Magic" (Queen, 1986), "She Blinded Me with Science" (Thomas Dolby, 1982), and "Here I Go Again" (Whitesnake, 1987). Each part of this series is named for an 80s song — a small mixtape playing under the trilogy.*
