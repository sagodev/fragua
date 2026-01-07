# Fragua

Fragua is a lightweight Python framework designed to **design, validate, and reason about ETL logic** in a fully controlled, in-memory environment.

It provides a minimal and explicit execution model where ETL functions are registered, composed, executed sequentially, and inspected — **without schedulers, persistence layers, or external infrastructure**.

Fragua is intentionally simple. Its goal is clarity over completeness.

---

## Purpose

Fragua exists to answer a small, focused set of questions:

> *Does this ETL function behave as expected?*
> *Does this sequence of ETL steps produce the correct result?*

It is **not** a workflow orchestrator nor a production-grade ETL engine.
Fragua is a **developer-oriented framework** for modeling, validating, and experimenting with ETL logic during development.

---

## Core Model

Fragua is built around a small set of orthogonal, loosely coupled components.

### 1. FraguaSet

A `FraguaSet` is a **logical namespace for functions**.

* Stores named callables
* Groups functions by purpose (e.g. `extract`, `transform`, `load`, `utility`)
* Contains no execution logic
* Has no knowledge of pipelines or data

Sets are created explicitly and only when needed.

---

### 2. FraguaRegistry

The registry is a **lookup and organization layer**.

* Holds multiple `FraguaSet` instances
* Resolves functions by `(set_name, function_name)`
* Does not execute anything

The registry enables flexible function categorization without hardcoded assumptions.

---

### 3. FraguaStep

A `FraguaStep` represents a **single declarative execution unit**.

* References a function by name (resolved at runtime)
* Declares execution parameters
* Optionally consumes the output of a previous step
* Stores its result under a logical key (`save_as`)

A step defines *what should happen*, not *how it happens*.

---

### 3.1 FraguaStepBuilder

A `FraguaStepBuilder` is a **mutable builder** for constructing immutable `FraguaStep` objects.

* Provides a fluent interface for step configuration
* Allows method chaining (`.with_params()`, `.with_save_as()`, `.with_use()`)
* Produces immutable steps via `.build()`
* Enables safe, incremental step construction

The builder reduces boilerplate while preserving step immutability.

---

### 3.2 FraguaStepIndex

A `FraguaStepIndex` is a **template registry** for preconfigured step builders.

* Stores `FraguaStepBuilder` templates by name
* Returns fresh builder copies from templates
* Enables discoverable step composition
* Provides safe access to registered step patterns

The index facilitates reusable step templates without sacrificing explicitness.

---

## 4. FraguaPipeline and PipelineBuilder

A pipeline is an **ordered execution plan**.

* Defines a sequence of `FraguaStep`
* Preserves execution order
* Contains no execution logic

`PipelineBuilder` and declarative compilation now allow:

* Adding multiple steps at once
* Defining pipelines with macros that expand automatically into steps
* Setting `save_as` for the final output of a macro for easy downstream use

Pipelines are pure definitions executed by an agent at runtime.

---

## 5. FraguaAgent

The agent is a **stateless execution primitive**.

* Receives a pipeline
* Resolves step functions via the registry
* Executes steps sequentially
* Produces execution results

The agent contains no domain logic and holds no state between runs.

---

## 6. FraguaWarehouse

The warehouse is an **in-memory result store**.

* Stores outputs of all executed steps
* Indexed by `save_as`
* Intended for inspection, debugging, and assertions

The warehouse exists purely at runtime.

---

## 7. FraguaEnvironment

The environment is the **composition and orchestration boundary**.

It owns:

* One registry
* One agent
* One warehouse
* One StepIndex

It provides APIs to:

* Create and manage function sets (optionally tagged to prevent step builder creation)
* Register functions and pipelines
* Compile declarative pipelines with macros
* Execute pipelines
* Retrieve execution results

The environment does not impose structure — it enables it.

---

## Helper Abstractions

### Macros and Declarative Pipelines

Macros (e.g., `transform_chain`) allow expanding multiple steps automatically. They can define a `save_as` for the last step, enabling downstream steps to reference macro output naturally.

### Automatic Step Generation

Functions like `create_transform_steps` generate sequences of `FraguaStep` from function names, chaining them automatically.

### Result Inspection

Helpers such as `get_box_dfs_heads` allow validated inspection of runtime results:

```python
heads = fg.get_box_dfs_heads(box_result, pipeline.steps())
```

Errors are raised if expected outputs are missing or invalid.

---

## Typical Workflow

1. Create an environment
2. Create one or more function sets
3. Register ETL functions into sets
4. Optionally compose transformations and macros
5. Define a declarative pipeline
6. Compile the pipeline
7. Execute the pipeline
8. Inspect results from the warehouse

---

## Design Principles

* **Minimalism** — no feature without a clear purpose
* **Explicitness** — no hidden behavior
* **Single Responsibility** — each component does one thing
* **Runtime-only** — no persistence, no side effects

---

## What Fragua Is Not

Fragua is not:

* A scheduler
* A workflow orchestrator
* A production ETL engine
* A data platform

It is a **developer framework for ETL design and validation**.

---

## License

MIT License
