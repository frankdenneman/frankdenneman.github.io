---
title: "Anatomy of an Agentic Workload"
linkTitle: "Part 2 - Anatomy of an Agentic Workload"
description: "What actually happens when an agent runs? From harnesses and tools to model calls and GPU execution, this article explains the components of an agentic workload and why 100 active agents don't necessarily mean 100 concurrent inference requests."
date: 2026-10-19
url: "/2026-10-19-anatomy-of-an-agentic-workload/"
series: ["Agentic Workloads"]
series_order: 2
concepts: ["AI Agents", "Agent Loops", "Tool Calling", "Workflow Automation", "Agent Runtime", "Infrastructure Automation"]
categories: ["ai"]
track: "Agentic Workloads"
aliases:
  - "/posts/2026-10-19-anatomy-of-an-agentic-workload"
  - "/2026-10-19-Anatomy-of-an-Agentic-Workload/"
  - "/2026-10-19-Anatomy-of-An-Agentic-Workload/"
  - "/2026-10-19-Anatomy-Of-An-Agentic-Workload/"
  - "/2026/10/19/anatomy-of-an-agentic-workload/"
---

## Anatomy of an Agentic Workload

[The previous article](https://frankdenneman.ai/2026-10-13-agent-or-flowchart-find-the-box-you-cant-finish-drawing/) explored when an agent makes sense. It reduced an agent to a loop: a model, a set of tools, and a condition that tells it when to stop. The interesting part was the ability to decide what to do next based on the result of the previous step.

But what actually happens when that loop runs, and which parts of the infrastructure are involved?

This article establishes the terminology used throughout the series. It explains triggers, harnesses, tools, skills, execution environments, and the model itself. Understanding how these components interact provides the foundation for examining how agentic workloads differ from human chat, and what those differences mean for GPU compute, memory consumption, scheduling, and cache locality.

## From answering questions to executing tasks

A typical chatbot interaction starts when a person submits a prompt. The inference server processes the input tokens, generates output tokens, and completes the request. The person reads the answer and decides what to ask next. The conversation may remain open, but the model is not continuously executing on behalf of that conversation.

Consider the bicycle example from the previous article: "Should I bike to Amsterdam tomorrow?" The chatbot cannot check the calendar, route, or weather forecast without access to tools. Instead, it asks for more information. The person checks the relevant details, submits another message, and repeats the process until there is enough information to make a recommendation.

![A chatbot trace showing sequential user and model interactions.](images/chatbot-trace.svg)

The diagram shows three model calls. Between those calls, the person checks the calendar, looks up the forecast, and provides the missing information manually. Each model request finishes before the next user message arrives. The pace of the conversation is determined by human interaction, not by the model.

Now consider the same question handled by an agent. Instead of asking the person to collect the missing information, the model can request actions through tools. The surrounding software executes those actions, collects the results, and sends them back to the model. The model uses that information to determine what to investigate next.

![Illustration of an agentic workflow with planning, tool execution, result inspection, and iteration.](images/bike-agent-loop.svg)

The agent starts by checking the calendar and route. A 09:00 meeting and a 20-kilometer journey establish the relevant departure time. The next step is to retrieve the weather forecast and evaluate the headwind along the route. When the result shows a 35 km/h headwind at 07:30, the agent investigates alternative departure times. A later departure turns out to be worse, while leaving at 06:45 provides better conditions and still fits the calendar.

The diagram shows four model calls and six tool calls, all initiated by a single user request. The model determines which information is needed, the tools retrieve or process that information, and the results influence the next step. The person no longer needs to perform the intermediate lookups. The important difference is not simply the number of model calls. The initial request starts a workflow that can continue without further human interaction. The next model request is triggered by the completion of a tool operation rather than by someone reading an answer and typing another question.

That distinction becomes interesting when looking at the infrastructure involved. Each model call requires inference, typically executed on GPUs. Checking the calendar, retrieving weather data, calculating the headwind along the route, and evaluating departure options are tool operations, generally executed using CPU resources or external services. An agent harness coordinates these activities and maintains the execution state (more about agent harnesses in the next section).

The GPU is not continuously busy throughout the agent run. Once a model call finishes, the agent harness may spend time executing tools or waiting for their results. During that interval, the inference server can process requests from other applications or agents. When the tool results arrive, the agent harness constructs another model request and execution continues.

There is another characteristic visible in the agent trace. Each subsequent model request needs enough context to continue the task. That can include the original question, instructions, previous model responses, and tool results. Some information is new, but much of the input may have already been processed during earlier model calls.

These execution patterns introduce three characteristics relevant to inference infrastructure. A single task can generate multiple model requests. Tool execution creates intervals between those requests, resulting in bursts of GPU demand rather than continuous execution. And repeated context creates opportunities to reuse previously computed inference state.

The following articles will examine the consequences for inference capacity, scheduling, and cache reuse. First, it is necessary to understand the components responsible for executing the agent workflow.

## Anatomy of an agent

![Agent anatomy showing triggers, harness, system prompt, skills, tools, sandbox, and shared model endpoint.](images/agent-anatomy.svg)

Consider an AI infrastructure Kubernetes operation. An administrator wants to upgrade the GPU driver on a Kubernetes worker node and asks: **“Can I drain gpu-node-07 now?”**

This looks like a simple yes-or-no question, but the answer depends on several systems. The node may be running inference replicas with active requests and cached context. A training job might span multiple nodes connected through a high-speed network. Other nodes might have free GPUs, but not enough capacity within the required NVLink topology.

The agent needs to collect information before recommending an action. Available GPU memory alone does not establish whether the node can safely be drained. The next check depends on what the previous check revealed, exactly the kind of problem discussed in the previous article.

### The trigger

One thing many articles and presentations seem to omit is the question what actually triggers an agent? Something has to start the agent. That might be a person entering a command, a monitoring alert, a scheduled maintenance workflow, or another agent delegating part of its work.

A person can start the drain agent directly through a CLI command, a Slack integration, or a button in an operations portal. There is also a less direct path. Imagine an administrator talking to a general-purpose infrastructure assistant. The administrator asks whether gpu-node-07 can be drained. The assistant has several tools available, including a specialized drain agent. The model selects that capability and returns a tool call requesting its execution.

The assistant's agent harness receives the tool call and starts the drain agent. The model does not independently discover arbitrary agents running somewhere in the infrastructure. The available capabilities have to be registered or exposed through the surrounding software.

The same drain agent could be invoked by a Kubernetes controller or a scheduled maintenance workflow. In all cases, the agent receives a task. What differs is the system responsible for starting it. A scheduled maintenance workflow could start one hundred agents at 02:00 without a single administrator being logged in. The number of agent runs is no longer necessarily connected to the number of people using the platform.

### The agent and its harness

The agent describes the task and the capabilities available to perform it. Typically, an agent configuration contains a system prompt, a set of tools, optional skills, and a reference to the model it should use. But a configuration does not execute anything. That is the responsibility of the agent harness.

**The agent harness is the program that runs the agent loop.** It assembles the model request, sends it to the inference endpoint, receives the response, and executes any requested tools. Tool results are added to the context before the next model call. The process continues until the model produces a final answer, an execution limit is reached, or another stopping condition applies. The simplest harness can be expressed in a few lines of pseudocode:

```python
while True:
    response = model(context)

    if response.tool_calls:
        results = execute_tools(response.tool_calls)
        context.extend(results)
    else:
        return response
```

A production agent harness also handles errors, tool-call arguments, context management, execution limits, permissions, and other operational concerns. But the underlying mechanism remains recognizable.

Several frameworks and applications provide this functionality. LangGraph offers a graph-based runtime for stateful agent execution. LangChain provides agent abstractions built on LangGraph. The OpenAI Agents SDK and Claude Agent SDK provide their own agent loops, tool integration, and execution controls.

OpenClaw and Hermes are also examples of agent harnesses, although they are packaged more as complete agent environments than as libraries for building workflows. They combine the agent loop with capabilities such as persistent sessions, tool execution, and integrations with communication channels. They can run as long-lived services, allowing agents to respond to messages and events without requiring a developer to start a new process for each task.

Organizations can use these frameworks, extend them, or build their own harness. A Python application that maintains context, calls a model, executes tools, and evaluates stopping conditions already implements the essential behavior.

From an infrastructure perspective, the harness is application software. It runs on a conventional operating system, manages state, makes API calls, and waits for responses. It does not execute the model's transformer computations itself. A developer tool might run the harness on a laptop. An enterprise service might run it inside a Kubernetes deployment. A larger platform might operate many harness workers concurrently.

The harness consumes CPU, memory, and network resources. Depending on the implementation, it may also require persistent storage for execution state and logs. It does not require a GPU simply to orchestrate the agent. The GPU-intensive work happens when the harness sends a request to the model.

This separation matters operationally. Agent harness workers can scale independently of inference replicas. Adding agent harness capacity allows more agent runs to execute, but it does not automatically increase the inference capacity available to them.

![agent vs inference scaling](images/harness-vs-replicas.svg)

### The tools

The model cannot inspect the state of a Kubernetes cluster by itself. It needs a way to retrieve that information. That is where tools come in. A tool is a function or service that performs a defined operation and returns a result. For the drain agent, examples include `get_node_workloads(node)`, `get_training_job_topology(job)`, `get_available_gpu_capacity(cluster)`, `get_inference_replica_state(node)`, and `get_node_health(node)`. The model decides which tool to call. The harness executes it and returns the result.

There is another reason to use tools beyond accessing external systems. **LLMs are reasoning engines, not calculators.**

Suppose the task is to determine whether a host is overloaded. One approach would be to retrieve thousands of CPU utilization samples, send the entire array to the model, and ask it to calculate the average and the 95th percentile. But why do that? A small Python function can perform those calculations quickly and deterministically. Instead of sending thousands of samples, the tool returns the relevant metrics:

```json
{
  "host": "gpu-node-07",
  "cpu_average_15m": 74.2,
  "cpu_p95_15m": 93.1,
  "threshold_exceeded": true
}
```

The model uses that information to decide whether CPU pressure matters to the investigation and what it should check next. Python performed the calculation. The model reasons about the result.

Tools can be implemented in two places. The simplest is a function in the agent harness's own code, as in the examples above. The other is a Model Context Protocol (MCP) server: a separate process or service that exposes tools over a standard interface, so that one tool implementation can serve any harness that speaks the protocol. A local MCP server runs as a child process of the agent harness. A remote one is an HTTP service, which makes it a workload in its own right: something to deploy, secure, and version, and something many agents can share, the same way they share the model endpoint. A single Kubernetes MCP server could serve the drain agent, a capacity-report agent, and an administrator's general assistant at once.

Two things follow for infrastructure. When a tool runs on an MCP server, that server's credentials and network reach define what the tool can do; the boundary has moved from the harness's sandbox to the server. And every tool, local or MCP, contributes its definition to the model's context on every request: name, description, and argument schema. Connect ten MCP servers with a dozen tools each and the model reads all of those definitions before it reads the task. The measurement later in this article shows what that costs.

This mirrors an observation from an [ITQ](https://itq.eu/nl/) hackathon. Several teams were building applications that used sensor data. Initially, they sent raw sensor readings directly to an LLM and asked it to interpret the measurements. The results were inconsistent. LLMs are reasoning engines, not calculators. The teams eventually introduced a small machine learning model to process the sensor stream. Instead of asking the LLM to work through the raw measurements, they exposed the ML model through a tool and passed its output to the LLM.

That changed the division of responsibility. The specialized ML model processed the sensor data. The LLM interpreted the outcome and decided what to do next. A Python calculation can provide a deterministic result, while a trained ML model produces a prediction or classification that may still have uncertainty. But the architectural principle is the same: **use specialized software to process data, and use the LLM to decide how the resulting information affects the task.**

This also reduces the amount of context sent to the model. Instead of thousands of raw measurements, the model receives a compact result. Tool execution introduces another important behavior: while a tool runs, the harness may be waiting for an API response, a command, or another service. During that period, the agent does not necessarily have an active inference request. The GPU can serve other requests while the harness waits.

### The system prompt

The system prompt defines the agent's role, scope, and intended behavior. For the drain agent, it might look like this:

```text
You plan node drains for GPU clusters.

The user names a node. Determine whether it can be
 drained now. If it cannot, explain why and list
 the available options.

Retrieve workload, capacity, topology, and health
information through the available tools.

Do not estimate infrastructure state.

When a workload spans multiple nodes, inspect the
relevant nodes before making a recommendation.

Recommend an action, but leave the decision to the user.

Do not terminate workloads or perform disruptive
actions without explicit authorization.

Stop when you can provide a supported go/no-go
recommendation, or after 20 tool calls.
```

Notice what the prompt does not contain. It does not describe every possible Kubernetes scheduling constraint, every GPU topology, or every procedure for relocating a training job. Those details belong in tools and domain-specific knowledge available to the agent. The prompt tells the agent what it is responsible for and how it should behave. It does not need to become an operations manual.

There is also an important security distinction. A prompt can instruct the model not to terminate production workloads, but that instruction is not a security control. If an agent must not terminate workloads, the execution environment should enforce that restriction through permissions, credentials, approval gates, and tool access. The prompt communicates the intended behavior. The infrastructure determines which actions are actually possible.

### Skills

A skill provides additional knowledge or procedures that the agent can use for a particular task. The system prompt defines the agent's responsibility, while a skill explains how to handle a specific situation within that responsibility.

For example, the drain agent might have access to a skill called `gpu-node-drain`:

```markdown
---
name: gpu-node-drain
description: Use when asked whether a GPU node can be drained, cordoned, or taken out of service for maintenance. Covers training jobs, inference replicas, and scheduled work on the node.
---

# GPU node drain

Work through every section that applies. A section applies when the
tool results show the node hosts that kind of work. Verdicts come from
tool results, never from estimates.

## 1. What is on the node

Call `get_pods_on_node(node)` and `get_node_health(node)`.
Classify each pod as training, inference, or other. If the node is
already unhealthy, say so: a failing node changes the cost of waiting.

## 2. Training jobs

For each distributed training job on the node:

1. Identify every node the job spans. `get_job_checkpoint_state(job)`
   returns the member list with the checkpoint state.
2. Check whether the job checkpoints, when it last did, and when the
   next checkpoint is due.
3. Check replacement capacity for the whole job, not for this node's
   share: `get_cluster_capacity(gpu_type, count, topology)`.
4. Confirm the replacement GPUs sit in one NVLink domain and on the
   fabric the job requires.

Free GPU count is not evidence that a job can be rescheduled. Eight
free GPUs spread over four nodes do not replace one node of eight.

A job that cannot checkpoint, or has no replacement capacity, is a
blocker. A job whose next checkpoint lands inside the maintenance
window is preparation: wait for it.

## 3. Inference replicas

For each replica on the node:

1. Get in-flight requests and cached context:
   `get_replica_cache_state(replica)`.
2. Check whether the router can stop sending new work to it.
3. Determine whether the in-flight requests can finish on their own.
4. Check replacement capacity for the replica: `get_cluster_capacity`.

Cached context is lost when the replica stops. Traffic that depends on
it pays full prefill elsewhere. Report that as a cost, not a blocker.

## 4. Scheduled work

Call `get_scheduled_jobs(node, window)`. A reservation or queued job
that lands on this node during the window is preparation: move it, or
shrink the window.

## Verdict

Return exactly one of:

- Safe to drain
- Drain possible after preparation
- Drain blocked

List the reasons. For preparation, list each step and who performs it.
```

The skill does not execute these steps itself. It provides instructions that the model can use to determine which tools to call and how to interpret the results. A skill can also include reference material, scripts, or other resources, depending on the agent harness implementation. Some agent harnesses load the full skill only when needed, while keeping a smaller description available so the model can decide when to use it.

![System prompt and skill are text the model reads; tools are code the harness runs. One model call uses all three.](images/prompt-skill-tools.svg)

The distinction is useful. The system prompt defines the agent's overall responsibility. The skill provides procedures for a particular domain or task. Tools retrieve information or execute operations. These are three different mechanisms, even though they work together during the same agent run.

### The sandbox

Tools sometimes need to execute commands, read files, or access infrastructure APIs. Those operations need an execution environment. For a developer running an agent locally, that is the developer's own shell: no boundary at all, which is the weakest form. For an enterprise deployment it is a container, pod, microVM, or VM with restricted access to the surrounding environment. This is commonly referred to as the sandbox.

The sandbox defines what tool execution can reach. For the drain agent, that might be read access to the Kubernetes API, the job controller, and the inference router, and nothing else. It should not inherit the harness host's permissions, and it should not reach every cluster or production system by default. Network policies, service accounts, filesystem restrictions, and short-lived credentials set the scope.

The reason this matters more for an agent than for any other service is in the loop itself. The model's output is executed, and every tool result flows back into the context the model reads next. A file, a ticket, or a web page that a tool reads can carry instructions, and the model has no way to tell those apart from yours. The prompt tells the model what it may do; the sandbox is where that limit holds when the model has been talked into something. The Hugging Face intrusion in section 2 is the case to keep in mind: the agent's permitted egress path was the hole.

Credentials are the clearest case. The tools need to authenticate to the Kubernetes API, the job controller, and the router, with an API key or a service account. The credentials belong in the sandbox: the tool code reads them from a mounted secret or an environment variable and attaches them to the call. The model never sees them. It produces the text `get_pods_on_node("gpu-node-07")` and nothing more; how that call was authenticated is the sandbox's business. That keeps the credentials out of the trace logs, out of every request to the model endpoint, and out of reach of anything a tool reads into the context. Because the sandbox exists per run, the credentials can be issued per run as well: read-only, valid for minutes, revoked when the sandbox is destroyed.

Lifecycle and scale are the operational half. The common enterprise pattern is one ephemeral environment per run: created at the first tool call, holding the run's working files, destroyed at the verdict. The context belongs to the harness; the working directory belongs to the sandbox. Two consequences follow from the numbers earlier in this article. The two hundred runs that start at 02:00 are two hundred sandboxes. And a cold start for a pod or microVM lands inside the tool-execution gap, the 5.2 seconds at the median in the trace, which is why warm pools of sandboxes exist.

One more boundary is easy to miss. Whatever a tool reads goes into the context, and the context goes to the model on every call. If the model is a hosted endpoint, that is data leaving your environment. The sandbox's read scope therefore doubles as the data-egress policy: anything it can read, the model provider can receive. Scope the sandbox to what the task needs, and have tools return the fields the verdict needs rather than whole objects.

Not every tool executes inside the harness's environment. Some run on MCP servers elsewhere, as described above. The boundary then sits on that server, and its permissions are the ones that count. What matters is knowing where each operation executes and which permissions apply at that point.

*Infrastructure consequence: sandboxes are workloads to place, secure, and manage, and they scale with runs the way harness workers do. Their startup time is part of tool latency. None of them need a GPU unless the tool itself runs a model.*

### The LLM

Please, look again at the agent anatomy diagram. The model is deliberately drawn outside the agent.

An agent does not need its own model deployment. The agent harness sends requests to an inference endpoint. That endpoint might consist of a single model server or several replicas behind a router. Other agents, applications, and ordinary programs can use the same endpoint.

The inference service does not need to know that a request belongs to a drain agent. It receives input tokens and generates output tokens, potentially including a request to call a tool. The agent harness interprets that output and decides how execution continues.

The model also does not own the agent's conversation history. The agent harness maintains the execution context and supplies the information required for each model call. The inference runtime may retain previously computed state, such as KV cache entries, but that is different from maintaining the agent's workflow.

The system has two distinct parts: the agent harness manages agent execution, while the inference platform processes model requests. Both can scale independently, but they are connected through the requests generated by the agent loop.

## From agent runs to inference requests

The components are in place. The trigger starts a run, the harness loops, the tools fill the gaps between model calls, and the model sees only requests. So the question for the inference platform is not how many agents exist but what those requests look like when the components run together. The bike example showed three characteristics: one task produces many model calls, tool execution puts gaps between them, and each call carries most of the previous one. Measurements of real agentic workloads put numbers on all three.

### An agent run is a sequence of model requests

In September 2026, the vLLM team published an analysis of the AgentX benchmark, which uses agentic coding traces. The reported workload had a median of 43 model turns per session. Each turn represents another interaction with the model, often followed by tool execution and another model request.

The same dataset reported that 44% of sessions contained at least one subagent. Among those sessions, the median number of subagent rollouts was four. Subagents introduce additional model calls that may overlap with the parent agent's execution.

One user task is no longer a single request followed by a human pause. It can become a sequence of dozens of model requests, with some generated by parallel branches.

Source: [vLLM x AgentX: Optimizing for Real-World Agentic Serving](https://vllm-project.github.io/2026/09/08/vllm-agentx.html).

### The gaps between model calls are not predictable

An analysis of Codex traces from SWE-bench Pro reported 610 traces with a median session length of 33 model turns. The median delay between turns was 5.2 seconds, while the 99th percentile reached 81.4 seconds. That is substantial variation.

During those intervals, the agent may be executing tools, waiting for external systems, or performing orchestration work. The inference server does not necessarily have an active request for that agent. This is where agent session concurrency and inference request concurrency diverge.

Imagine one hundred agents running simultaneously. If most are waiting for tools, only a small number may be using inference capacity. When several tools finish around the same time, the harnesses submit their next requests and inference concurrency increases. If those agents also delegate work to subagents, a single run may produce several overlapping model requests.

The inference platform sees bursts of requests separated by intervals of little or no activity from those same sessions.

Source: [Serving Agentic Workloads at Scale with vLLM x Mooncake](https://vllm.ai/blog/2026-05-06-mooncake-store).

### Each model request can carry substantial context

There is another difference between counting requests and understanding their cost. A measurement of Claude Code's first request in an empty directory found 23,207 input tokens before the agent had read a project file or performed meaningful work. After removing tool definitions and the tool definitions from connected MCP servers, the request contained 2,664 tokens.

The measurement was performed on one specific Claude Code configuration, so the numbers are not representative of every agent. But they demonstrate that the harness can introduce substantial context before the task itself begins.

The AgentX analysis reported a median input length of 142K tokens and a median output length of 444 tokens, with more than 96% prefix-cache hits in the measured serving workload. The Codex/SWE-bench Pro analysis separately reported an average input-to-output token ratio of approximately 131:1.

These are different datasets and should not be combined into one synthetic workload. They do, however, illustrate a consistent characteristic: agentic coding workloads can generate long input contexts, relatively short outputs, and substantial repeated context across turns.

Sources: [Claude Code first-request measurement](https://dev.to/rulestack/claude-codes-disallowedtools-skill-dropped-18962-characters-of-skill-listing-and-saved-only-lga), [vLLM AgentX](https://vllm-project.github.io/2026/09/08/vllm-agentx.html), and [vLLM Mooncake](https://vllm.ai/blog/2026-05-06-mooncake-store).

### What does the inference platform actually see?

![An agent execution trace showing model calls, tool execution, and parallel branches.](agent-request-flow.svg)

The execution trace illustrates why an active agent cannot be treated as one continuously running inference request. The model is called, produces a result, and the harness continues with tool execution. During the tool call, the agent remains active but may not consume inference capacity. When the result returns, another model request is submitted.

Other runs can take different paths. Some finish after a few model calls. Others require dozens. Some delegate work and temporarily generate several requests in parallel.

For infrastructure operators, three different quantities matter:

- **Active agent runs:** How many tasks are currently being executed by harnesses.
- **Inference request rate:** How frequently those harnesses submit model requests.
- **Concurrent inference requests:** How many model requests are in flight at a particular moment.

These quantities are related, but they are not interchangeable. Even inference concurrency does not fully describe GPU demand. Two requests can have very different input lengths, output lengths, and cache reuse characteristics. They may occupy different amounts of GPU memory and require different amounts of computation.

This is why counting agents is not enough to size an inference platform. The harness determines when the model is called. Tools introduce pauses. Parallel execution introduces bursts. Software-driven triggers can start many runs independently of human activity. The inference platform must handle the requests those activities generate, not simply the number of agents that happen to be running.

## Closing

An agent is not a model with a different name. It is a software system that coordinates model calls, tools, and execution state to complete a task.

The trigger starts the run. The harness manages the loop. The system prompt defines the agent's responsibility. Skills provide domain-specific procedures. Tools retrieve information and execute operations. The sandbox and surrounding infrastructure enforce execution boundaries. The model is a shared inference service that the harness calls when reasoning is required.

Once these components are separated, the infrastructure implications become easier to understand. One hundred active agents do not necessarily mean one hundred concurrent inference requests. The number can be much smaller while agents wait for tools, or larger when work is delegated and executed in parallel.

That is the first change agentic workloads introduce: inference demand is shaped by software execution rather than primarily by human interaction.

The measurements from AgentX and the Codex traces reveal another characteristic. Agentic workloads repeatedly send large input contexts, often containing information that the model has already processed during earlier turns. If most of the input has been processed before, why should the inference server perform the same computation again?

The next article examines how repeated context changes the workload, why prefix caching matters, and how replica selection determines whether previously computed state can be reused.


