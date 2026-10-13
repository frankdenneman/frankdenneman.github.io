---
title: "Agent or Flowchart? Find the Box You Can't Finish Drawing"
linkTitle: "Part 1 - Agent or Flowchart?"
description: "Explains when an agent is actually useful by separating fixed workflow logic from the parts where the model must decide what to do next based on intermediate results."
date: 2026-10-13
url: "/2026-10-13-agent-or-flowchart-find-the-box-you-cant-finish-drawing/"
series: ["Agentic Workloads"]
series_order: 1
concepts: ["AI Agents", "Agent Loops", "Tool Calling", "Workflow Automation", "Agent Runtime", "Infrastructure Automation"]
categories: ["ai"]
track: "Agentic Workloads"
aliases:
  - "/posts/2026-10-13-agent-or-flowchart-find-the-box-you-cant-finish-drawing/"
  - "/2026-10-13-Agent-or-Flowchart-Find-the-Box-You-Cant-Finish-Drawing/"
---

## Agent or flowchart? Find the box you can't finish drawing.

I have spent a while trying to answer a simple question: what is an agent actually good for?

Most examples I see don't convince me. They look like ordinary programs with an LLM inserted into the control path. A tool gets called, a result comes back, and the model decides what happens next even though a developer could have written that decision in code. We've spent decades learning how to build reliable software by making control flow explicit. If the path is known, put it in code. If a decision is deterministic, make it deterministic. Handing that work to a model does not automatically make the system better.

So I started from the opposite direction: assume the 'traditional' program is the right answer. Where does that stop working? Almost any business process can be drawn as a flowchart. Most of the boxes are straightforward: call this system, check that value, run this calculation, ask for approval. Then you reach a box that says something like "investigate," "review," or "handle exception." That is the interesting box.

Not because it possibly contain a reason to introduce and agent and a LLM, but because the person doing that work does not follow one fixed path. They look at what they find, decide what matters, check something else, and keep going until they understand the situation. That is where an agent may have real value.

The question is not whether you can automate the process. We already know how to do that. The question is whether you can reasonably define the path in advance, or whether the path has to be discovered while the work is happening. That is the case I want to test in the rest of this article.

First, strip an agent down to the actual mechanism: the loop. Then look at the simple examples that are called agents today and ask whether that loop is doing anything useful. Finally, compare them with cases where the next step really does depend on what was discovered along the way.

## The loop

Strip away the SDKs and an agent is this:

```python
while True:
    response = model(context)
    if response.tool_calls:
        context += run(response.tool_calls)
    else:
        return response
```

A model, a set of tools, that loop, and a stop condition: the model answers without calling a tool, or you hit the maximum number of turns. That's the whole thing.

In the OpenAI Agents SDK, the `Agent` class is a configuration object for this loop: instructions, tools, model. `Runner.run` is the loop itself. Handoffs, guardrails and tracing are scaffolding around it. Strip away the framework features and most agent runtimes eventually reduce to some variation of this loop.

## The hello-world agent

[OpenAI's documentation](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) introduces agents like this:

```python
weather_agent = Agent(
    name="Weather agent",
    instructions="You are a helpful agent who can talk to users about the weather",
    tools=[get_weather],
)
```

My reaction when I first saw this: that's an API call. `get_weather` takes a city and returns a forecast. Wrapping it in something called an agent doesn't change what it does. Follow it at runtime. A user asks about the weather in Amsterdam. The model emits `get_weather("Amsterdam")`. The tool runs. The result is appended to the context. The model writes a sentence.

The agent completes one tool round: model, tool, model, done. The model's only decision was "call the tool, and with which argument." Now compare it with the weather app on your phone. You type a city, it calls the same API, it shows the forecast. No model anywhere, no tokens spent.

In the most positive way, what the agent adds is that you can type "what's it like in Amsterdam tomorrow?" instead of "Amsterdam," and get a sentence back instead of a screen. For some, that might be useful. It is also two small language tasks, pulling the city out of the question and phrasing the answer, bolted onto an API call and consuming tokens along the way.

If you look beyond the hype, and deal with the question 'How can we reduce token spending' on a daily basis, we must acknowledge that not everything needs a model, and some the parts of a business process do don't need a loop.


## When an agent loop starts doing real work

Change the question and widen the vocabulary.

"Should I bike to Amsterdam tomorrow?" requires an LLM with tools such as get_weather, get_route and get_calendar.

Now the model has work to do. Which hour matters depends on what the calendar returns. A meeting at 09:00 means the forecast at 07:30 is the one that counts, not the daily summary.

This is also where context awareness starts to matter. The same weather does not mean the same thing in every situation. If you live in California, it may barely affect whether you get on a bike. In the Netherlands, a strong headwind can turn an easy 20 km ride into twenty kilometres of questioning whether it is time for a vacation.

That only becomes clear once the route and weather are considered together. A strong tailwind is very different from a 35 km/h headwind, so the model checks the route heading, compares it with the wind direction for that hour, then looks at whether there is a drier window and whether the calendar allows arriving later. This is domain knowledge that is not encoded in the workflow. A procedural system would need those relationships written down explicitly: if the route points west, compare it with wind direction; if the meeting starts at 09:00, check the weather around the departure time; if there is rain then, look for another window.

The model can reason about those relationships without every branch being represented in workflow code. That is the important distinction. That distinction matters because the word "agent" is used for two different things: the object you create in an SDK, and the behaviour you actually want from the system.


## One word, two meanings

- `Agent` the class: an LLM configured with tools and run in a loop. For example, the `weather_agent = Agent(...)` object from the earlier code. It says nothing about whether the loop is actually needed for that task.
- Agent the behaviour: the loop iterates more than once, and the model chooses the next tool based on intermediate results in a way you could not have planned in advance.

Every SDK example is the class. Almost none shows the behaviour, because examples have to fit on a slide. The diagnostic for any agent you're shown is simple: does the model ever need to decide what to do next based on what just came back?

If not, the path was already known.

In that case, keep the useful language part, but put the sequence back in code. A fixed workflow is easier to test, easier to bound, and usually cheaper to run. The loop only earns its place when the next step cannot be known until the previous one has finished.

## The same loop in the datacenter

"Can I put esx-07 into maintenance mode now?"

Tools: `get_vms_on_host`, `get_vm_constraints` (affinity rules, passthrough devices, vGPU profile), `get_cluster_capacity` (effective, after HA admission control), `get_host_health`, `get_scheduled_jobs`.

Follow the run.

The model lists the VMs on 07. Constraints show three of them in an anti-affinity group spread across 07, 03 and 05. Nobody asked about host 03, but the model checks its health, because the rule can only be honoured after evacuation if 03 can take a VM. It finds 03 degraded. That's a blocker that exists only because of another host's state.

One VM carries a vGPU. Which hosts have a compatible profile with a free slot? Capacity: 40% raw free, but much less of it is actually usable once HA reservations and the vGPU placement constraints are applied. And a backup window opens at 22:00; sixty vMotions on the shared 10GbE will land inside it.

Recommendation: not now.

Options: evacuate after 23:30, power off VM X (needs its owner), or relax the anti-affinity rule for the duration.

The headwinds here are 03's state, HA reservations, the vGPU profile and the backup window. None were in the question. The order was content-driven: the anti-affinity finding triggered the host-health check; the vGPU finding changed what "capacity" meant.

This is where the agent fits into the existing infrastructure workflow. DRS already does the deterministic version. It evacuates the host, or it fails with "insufficient resources," and then the admin spends half an hour finding out why.

This is where the agent becomes useful. It does the investigation an admin would normally do after DRS fails, but before anyone starts maintenance mode. It brings the relevant state together, follows the blockers it finds, and turns that into a recommendation. The admin still decides whether to proceed. If you later allow the agent to take action itself, you can keep that scope narrow: proceed only when there are no blockers and no power-offs are required. Anything outside that stays with the admin.

## Why an agent instead of a flowchart

This is the real design question, and the answer is short. In a normal program, you define the path in advance: if this happens, check that; if that fails, try something else. With an agent, you define the tools it can use and let the model decide which one to use next. That is the important difference.

A procedural system needs the relationships between conditions and actions explicitly encoded. The model can reason about those relationships without every possible branch being written into the workflow. The useful part is that it is much easier to define what the model is allowed to look at than to describe every path it might need to take.

"What would an expert look at?" has a short, stable answer: the VMs, their constraints, the cluster's real capacity, the other hosts, the schedule. "What should I check next?" depends on what the previous check returned. It changes with every environment and every incident, and a flowchart that tries to capture it grows a branch per incident until nobody can maintain it. So you still do the design work. You just specify the tools instead of the paths.

Two rules for the tool list.

1. Expose state at the granularity an expert asks for. `get_cluster_capacity` should compute admission control in code and return the effective number, not dump raw metrics for the model to reason over. Deterministic work belongs in the tool, not in the loop. Every calculation you push into a tool is a turn the model doesn't take.

2. Test the set by asking whether a competent admin who has never seen your environment could answer the question with only these tools. Missing one: add it. Answerable with one call: it's a function, not an agent.

## Agent or flowchart: the test

Now go back to the flowchart. Every box that needs language, pulling the city out of a question, reading a document, writing the summary, is one model call inside the program. The sequence stays in code.
That is not an agent, and most of what gets called one is exactly this.

You need the loop only for a box you can't finish drawing: what happens next depends on what came back, and the possible next steps are too many to write out and keep current. That one box is the agent. Everything around it stays a program.The bike ride and the maintenance mode both have that box, and they share four ingredients:

1. A go/no-go question.
2. State spread across several sources.
3. Checks whose relevance depends on earlier results.
4. Domain knowledge that is not encoded in the workflow. Headwind. The fact that raw free capacity and usable evacuation capacity are not the same thing.

If an example you're shown has all four, the loop is doing something. If it has one tool and one turn, it's an API call wearing a name badge. Keep it a program. The program handles the case where everything is fine. The agent handles "why won't it be fine, and what are my options?"

That's the one place the loop pays for itself: the path differs every time, the checks are cheap reads, and the action at the end is still a human's. If you can write down the path, keep it in code. If the next step depends on what you discover along the way, that is where the agent starts to earn its place.
