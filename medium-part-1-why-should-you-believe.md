# Promises, Promises — Why Should You Believe?

### Part 1 of 2. You can't command an LLM. You can only elicit a promise, then assess it. Why a twenty-year-old theory is the right foundation for agentic software, from someone who watched the same shift remake another field once before.

*By Jeremy Schulman*

---

I promise to blow your mind. I know how that lands: you have no reason yet to
believe me. Good. *Trust, but verify.* Hold onto that instinct; it's the whole
point, and we'll get there.

I've had an "Ah, Ha!" moment. Across two pieces I want to take you all the way
to the "Cha, Ching!", to the point where you can put into practice what you are
going to read about. This is not about another shiny demo or agentic
development framework. I want to share with you an entirely different _approach_ to
building sophisticated agentic solutions.

This first piece makes the case. The next piece, [Contracts, Not Prompts: How to Build an Agent You Can Prove](#), shows you the
way.

**TL;DR:** if you just want to look at a GitHub repo: `<Github repo: TBD>`.

## The Promise of Autonomous BPA

For almost two years I've been building and running in production something the
enterprise world has long, and frankly boringly, called **business process
automation**, or BPA. In the Era of AI, I am creating *autonomous* BPA. These
solutions act on their own, end to end, inside limits I can prove. Stateful,
multi-step, safety-sensitive systems that carry real organizational work. While
much of what you read about AI talks about copilots, chatbots, coding
assistants, and other such personal-productivity tools, I've been automating the
boring stuff, and building it in a completely different way.

My "customers" are the business units I serve.  They want outcomes regardless if
AI is used on the inside. Executives need to understand whether the money going
into AI is showing up as material business value. Autonomous BPA speaks to both:
it delivers the effect of *added staff*, value at the level of the whole
organization. Before AI, the sheer complexity of these use-cases kept them off
the table. The workflows were too tangled, too full of institutional knowledge,
to automate the old way. In 2025, for me at least, AI became the enabling
technology that finally makes creating them possible.

Along the way I worked out a technique for building
them that I haven't seen anywhere else. So I'm not talking hypotheticals. I'm
going to *show* it to you, and hand you the means to try this out for yourself.

So let me start with the assumption I think we're all quietly building on, and why it's broken: **that if we just write the instructions carefully enough, the machine will do as it's told.** It won't. It can't. **You cannot command an LLM. You can only elicit a promise and then verify it.** The teams who accept that *first*, who stop trying to command their agents and start doing something fundamentally different, are going to build the systems everyone else spends the next few years catching up to.

Here's the "Cha, Ching!", concretely, so you know what I'm actually going after.
One of the two example agents I'll show you (in the Github repo), which I call
**The Clinic**, takes "I'm Ada Lovelace, book me a dermatology visit"* and turns
it into a confirmed, eligibility-checked appointment, through real identity
verification, a coverage check, and an actual scheduling API. And it **provably
cannot** reach a state where it books before you're verified, or double-books a
slot. Not because I asked it nicely in a prompt. Because the design makes those
bad states unreachable*, and I can prove it, exhaustively, before I ever deploy.

That *"and I can prove it"* is the whole game. It's the thing a prose prompt can never give you. And make no mistake, something big is happening: agentic software is going through a paradigm shift. Let me tell you how I got here.

## I've seen this before

This post is going to talk about building agentic systems in a whole new way.
The concepts in it will change your life. They changed mine. 

I've said almost exactly those words before. Here's how I opened a blog post in
April 2013, back at Juniper Networks, when the subject was network
infrastructure management:

> *"This post is going to talk about managing networks in a whole new way. The concepts in it will change your life. They changed mine. There is no doubt that something big is happening. Our industry is going through a paradigm shift."*

I was right. I bet my career on that sentence and never looked back, and I didn't just *watch* that shift happen. I was part of a passionate group of people around the world who set out to help change the industry, and did. So when I tell you the same thing now, about agents, it isn't hype. It's pattern recognition from someone who has crossed this exact bridge once before: from a neighboring discipline into a field that wasn't ready for it.

Back in 2012 I was at Juniper Networks, deep in the Junos software world, when the head of networks at a Fortune 5 company asked me to make Puppet run on a switch. This was no idle question; a major sales deal hinged on the answer. My honest first reaction was, *"What is Puppet?"*

Then I looked, and the floor shifted under me. The sysadmins and the DevOps crowd had quietly gone through an entire revolution while the networking world wasn't paying attention. They'd stopped hand-configuring servers one at a time and started treating infrastructure as *code*: declarative, version-controlled, automatically enforced. The tools getting all the attention were **Puppet** and **Chef**, friendlier, wrapped in approachable languages that made the whole thing feel easy. But here's a detail whose weight I'd only feel years later: that entire declarative, desired-state model traced back to **CFEngine**, built in 1993 by a physicist named **Mark Burgess.** Puppet was a friendlier take on the paradigm he pioneered. And while the newcomers took the spotlight, CFEngine was quietly running some of the largest deployments on earth, single installations north of a million machines. The foundational tool wasn't the famous one. Hold that name: it's the same Mark Burgess whose *Promise Theory* is the backbone of this article. His fingerprints were on the last paradigm shift I lived through, too. I just didn't know it yet.

And it was obvious, standing there, that the same wave was about to hit networking whether the networking industry was ready or not.

Part of why I could see it coming was my unique role.  I had my feet in two
worlds. I reported into the Junos engineering software team, learning from Phil
Shafer (who essentially invented Junos automation), but my actual job was out in
the field with the sales team, using my engineering depth to help sell the value
of Junos. I have a split-brain mind - technologies, and go-to-market business.
Working across that boundary *was* the role. So much so that when I wrote the
whole thing up in 2013, I called it "Bridging the Two Worlds." I've stood
between worlds my whole career, which is probably why, years later, Mark's
border-crossing ideas would feel like coming home.

I wasn't guessing, and I wasn't alone. At PuppetConf in 2013, John Willis, the
mentor who gave me that "Ah, Ha!" to "Cha, Ching!" phrase, pulled me aside and,
in effect, handed me a crystal ball: *this* is what the next ten years of your
career look like, he said, if you commit to the network-automation movement. I
committed. And I had good company: Scott Robohn, my first manager at Juniper
back in 2008, would go on to co-found the Network Automation Forum. My friend
Peter Sprygada and I co-wrote the Puppet "netdev" module together; Peter went on
to become the driving force behind Ansible's network automation, the reason so
much of the world's network infrastructure is automated the way it is today. I
mention them because the point that matters for *this* article isn't that I
*noticed* a paradigm shift; it's that I was in the room, often near the front of
it, while one was made. I know what the early days of a real shift feel like
from the inside. 

They feel like that right now.

Here's the part of that story I want you to hold onto, because it turns out to
be the whole point of *this* article. The vision at the time was to run **Puppet**, the
sysadmins' own automation tool, natively on the switch, so that when they rolled out
an application, the network changes it needed rolled out *with* it: no ticket,
no waiting on the networking team. And if the rollout went sideways, a single
rollback reverted the application *and* the network together, as one unit. That
was the truly game-changing part. The reason it actually *worked*, the reason
the networking team could hand over that power without living in fear, came down
to two ideas:

1. **Scoped authority.** Role-based access control that said, precisely, *who can do what.* Puppet didn't get the whole network. It got exactly the slice it needed.
2. **A guarantee underneath.** As I wrote back then, the networking team was comfortable handing over control because *"Junos can guarantee at the OS level that [Puppet] won't harm the network."*

Read those two ideas again with 2026 eyes. You give an autonomous actor **scoped authority** to act, and you put a **deterministic layer beneath it that guarantees it cannot cause harm, no matter what it tries.** You don't trust the actor. You trust the guarantee.

I've been designing systems around that principle for thirteen years. An LLM
agent is just the newest, strangest, most capable actor I've ever been asked to
hand the keys to. And when I started building agentic based solutions, I
promptly forgot my own hard-won lesson.

## The wall: I forgot my own lesson

Here's the kind of instruction I started out writing. I'd bet you've written one just like it:

> *"You are a helpful clinic assistant. Always verify the patient's identity before booking anything. Never book an appointment that isn't covered without confirming self-pay first. Never double-book a time slot."*

It reads beautifully. It sails through a design review. Everyone nods. And it is **impossible to verify.**

I learned that the way everyone learns it: in the logs. The agent booked an appointment before it verified who it was talking to. It offered a slot, the slot got taken, and it cheerfully booked a *different* time nobody asked for. Each time, I did the thing we all do: I went back to the prompt and added another sentence. *"Really, always verify first."* *"Do NOT book a different slot."* I was negotiating with it.

And one day it hit me that I was making the exact category mistake I'd spent a decade warning networking teams about. I was writing those instructions as if the words were *commands* the model would *execute.* But that's not what an LLM is. It's a stochastic sampler. On any given turn it can classify intent wrong, skip a step, or invent a tool argument. No wording fixes that, because the wording was never the problem. **A prompt is not a command. It's a request, a hopeful one.**

For a one-shot Q&A bot, who cares: a wrong turn is cheap and the next question resets everything. But for a **stateful, multi-step, safety-sensitive** agent, one that touches money or identity or anything you can't undo, that category mistake is the origin of every incident that keeps you up at night. Because it leaves the one question you actually need answered completely unanswerable:

> *Can this agent ever reach a state it must never be in?*

With a prose prompt, the most honest answer I could give was: *"Probably not. But I can't prove it."*

I hate that answer. It's the "oh crap, is it the network?" of agent design: the sinking feeling that something's wrong and you have no way to know whether your own system is the cause. I'd forgotten what made 2013 work: you don't make the actor trustworthy by asking nicely. You put a guarantee underneath it. So I went looking for the agentic version of that guarantee.

## The reframe: an LLM is an autonomous agent

What unstuck me wasn't an AI paper. It was a body of work called [**Promise Theory**](http://markburgess.org/promises.html), developed by [Mark Burgess](http://markburgess.org/) and formalized with Jan Bergstra. It's about two decades old, and, this is not a coincidence, it comes from the very same configuration-management and distributed-systems world that gave us Puppet and Infrastructure as Code in the first place. The neighboring discipline came to my rescue twice in one career, and both times, it turned out, through the same man's ideas.

Here's something worth sitting with before we go further. Burgess spent the better part of twenty years developing Promise Theory, and for most of that time it lived at the margins, precisely *because* it refuses to stay inside one discipline. It draws on physics, on logic, on distributed systems, on the plain study of how autonomous things cooperate. Ideas that travel across borders like that are the easiest for any single field to wave off as "not our department." They're also the ones that, when someone finally listens, turn out to explain the thing nobody else can. Promise Theory was built to reason about autonomous agents more than a decade before the most important autonomous agent any of us would ever build (the LLM) even existed. It was *right,* and it was *early,* and it was *waiting.* I'm listening now. I think you should too.

Promise Theory reasons about systems built from **autonomous** parts, and its founding axiom is deceptively simple:

> An agent is autonomous. It can only make promises about *its own* behavior. No other agent can impose a promise upon it.

You cannot *force* another agent to do anything. You can only ask, and it decides. Promise Theory gives that ask a name: an **imposition.** A command, a hint, a request: all impositions, and all of them guarantee exactly nothing, because the target is autonomous. The only thing an agent can genuinely give you is a **promise:** a declaration about *itself* that you, the recipient, can then rely on and (here's the load-bearing word) **assess.**

Now read that axiom again with an LLM in mind, because this is where I sat up straight:

**Everything Promise Theory says about autonomous agents is true of an LLM as a matter of engineering fact, not as a metaphor.**

- You cannot impose behavior on it. No prompt *guarantees* an action.
- The most a prompt can do is *elicit a promise* to behave a certain way. Because the promiser is stochastic, you the recipient **must** verify.
- It is one autonomous agent among several: the model, the code around it, the external APIs, the human. There is no privileged commander in the room.

That's the reframe, and it changed how I build. Teams that treat prompts as commands spend their lives asking "why won't it obey?" Teams that treat prompts as **promises requiring assessment** build the guarantee on day one. I'd been living in the first camp, having forgotten I already knew how to live in the second.

If you take one idea from this article, take this one: **you can't command an LLM. You can only elicit a promise and then assess whether it was kept.** I've started calling the whole approach that follows from it **promise-and-assess.** It's the direct descendant of "hand over scoped authority, guarantee no harm underneath."

## The idea is only half the battle

Here's where most write-ups about Promise Theory and AI stop. They land the reframe, quote the axioms, and leave you nodding, with no idea what to do Monday morning. That gap is exactly where the real work lives. "Treat your LLM as an autonomous promiser" is a beautiful idea and completely inert until you can answer: where does the promise *live?* What file is it in? How do you check it? How does it survive contact with a real framework and a real deploy?

I spent the last year answering that, and built it into an open-source kit you can run today. That's the companion to this piece: **[Contracts, Not Prompts: How to Build an Agent You Can Prove](#)**. In it I show you the whole method: the single contract document that a model checker, your build code, and the LLM all read from; the state machine that proves The Clinic can never book before you're verified; and the enforcement code that keeps a stochastic promiser honest.

For now, hold onto the instinct I asked you to keep at the very top. Why should you believe an LLM's promise? You shouldn't, not on its own. You elicit the promise, and then you verify it. *Trust, but verify.* Here, that isn't a proverb. It's the whole method, and it's buildable. Let me prove it to you.

---

*With deep gratitude to Mark Burgess, whose Promise Theory is the foundation everything here is built on. If this piece did its job, go to the source: his* [Book of Promises](http://markburgess.org/BookOfPromises.pdf) *(the full* Promise Theory: Principles and Applications*, with Jan Bergstra, free to read online), and the more approachable* Thinking in Promises *(O'Reilly).*

*I've not yet had the pleasure of meeting Mark; by the time these words find their proper audience, I hope that's changed.*
