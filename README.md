# Fragua

Fragua is a lightweight Python library designed to **test and validate ETL functions** in isolation.

It provides a minimal execution environment where ETL functions can be registered, executed, and their results inspected at runtime — without introducing framework overhead, persistence layers, or external dependencies.

Fragua is intentionally simple by design.

---

## Purpose

Fragua exists to answer a single question:

> *"Does this ETL function behave as expected?"*

It is not an orchestration engine, scheduler, pipeline runner, or data platform.
It is a **focused testing tool** for developing and validating ETL logic.

---

## Core Concepts

Fragua is composed of seven small components:

### 1. FraguaSet

A `FraguaSet` is a **namespace for ETL functions**.

* Stores named callables
* No execution logic
* No awareness of environments or data

Typical sets are:

* `extract`
* `transform`
* `load`

---

### 2. FraguaRegistry

The registry is a **function index**.

* Holds multiple `FraguaSet` instances
* Resolves functions by `(set_name, function_name)`
* Performs no execution or validation

---

### 3. FraguaAgent

The agent is a **pure executor**.

* Receives an serie of steps that each step represent an function
* Executes the steps pipeline
* Returns the result

The agent contains no domain logic and no state.

---
### 4. FraguaPipeline

The pipeline represents an **ordered execution plan**.

* Defines a sequence of execution steps
* Preserves execution order
* Is fully declarative and contains no execution logic
* Can be reused, inspected, or validated before execution

A pipeline does not execute functions by itself.  
It is consumed by an agent at runtime.

---

### 5. FraguaStep

A step represents a **single unit of execution** within a pipeline.

* References a function by action and name
* Declares execution parameters
* Optionally consumes data produced by a previous step
* Optionally stores its result under a custom key

A step contains no executable logic.  
It only describes *what* should be executed, not *how*.

### 6. FraguaWarehouse

The warehouse is an **in-memory store for execution results**.

* Stores results produced during runtime
* Indexed by a logical execution key (e.g. `extract.from_csv`)
* Intended for inspection, assertions, and debugging

No persistence, security, or lifecycle management is included.

---

### 5. FraguaEnvironment

The environment is the **only orchestration layer**.

It owns:

* One agent
* One registry (function sets)
* One warehouse

It provides a small public API to:

* Register functions
* Execute step(functions) pipelines
* Access stored results

---

## Typical Workflow

1. Create an environment
2. Register ETL functions
3. Execute steps pipeline
4. Inspect results from the warehouse

---

## Example

```python
from fragua.core.environment import FraguaEnvironment

# Create environment
env = FraguaEnvironment("demo")

# Define ETL function
def extract_users(path: str) -> list[str]:
    return ["alice", "bob"]

# Register function
env.register_function("extract", extract_users)

# Execute
result = env.run("extract", "extract_users", path="users.csv")

# Inspect result
assert result == ["alice", "bob"]

stored = env.warehouse.get("extract.extract_users")
assert stored == result
```

---

## Design Principles

Fragua is guided by the following principles:

* **Minimalism** — no feature without a clear purpose
* **Single Responsibility** — each component does one thing
* **Runtime-only** — no persistence or side effects
* **Explicitness** — no hidden magic or implicit behavior

If a feature does not directly support ETL function testing, it does not belong in Fragua.

---

## What Fragua Is Not

Fragua deliberately avoids being:

* A workflow orchestrator
* A scheduler
* A pipeline framework
* A data warehouse
* A production ETL engine

It is a **developer tool**, not an execution platform.

---

## When to Use Fragua

Use Fragua when you want to:

* Test ETL functions independently
* Validate transformations in isolation
* Inspect intermediate results
* Develop ETL logic incrementally

---

## License

MIT License
