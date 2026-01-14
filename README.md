# Fragua

[![Python Version](https://img.shields.io/badge/python-%3E%3D3.10-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Fragua is a lightweight Python framework designed to **model, validate, and execute ETL logic** in a fully controlled, in-memory environment.

It provides an explicit and minimal execution model where **ETL functions, declarative pipelines, and macros** are composed and executed deterministically — **without schedulers, persistence layers, or external infrastructure**.

Fragua intentionally prioritizes **clarity over completeness**.

## Installation

```bash
pip install fragua
```

---

## Purpose

Fragua exists to answer a focused set of development-time questions:

> *Does this ETL function behave as expected?*  
> *Does this declarative pipeline produce the correct result when executed?*

Fragua is **not** a workflow orchestrator nor a production ETL engine.  
It is a **developer-oriented framework** for designing, validating, and reasoning about ETL logic during development.

## Quick Start

```python
import fragua as fg
import pandas as pd

# Create environment
env = fg.FraguaEnvironment(name="my_etl")

# Define functions
def extract_data() -> pd.DataFrame:
    return pd.read_csv("input.csv")

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna()

def load_data(df: pd.DataFrame) -> None:
    df.to_csv("output.csv", index=False)

# Register functions in sets
extract_set = env.registry.create_set("extract")
transform_set = env.registry.create_set("transform")  
load_set = env.registry.create_set("load")

env.add_sets(extract_set, transform_set, load_set)
env.add_functions(extract_data, set_name="extract")
env.add_functions(transform_data, set_name="transform")
env.add_functions(load_data, set_name="load")

# Define and execute pipeline
pipeline = {
    "name": "simple_etl",
    "steps": [
        {"set": "extract", "function": "extract_data", "save_as": "raw_data"},
        {"set": "transform", "function": "transform_data", "use": "raw_data", "save_as": "clean_data"},
        {"set": "load", "function": "load_data", "use": "clean_data"}
    ]
}

result = env.execute_pipeline(pipeline)
print(result.metadata)
```

---

## Core Architecture

Fragua is built around a small number of orthogonal, loosely coupled components with strictly defined responsibilities.

---

## 1. FraguaSet

A `FraguaSet` is a **logical container for executable definitions**.

* Stores named **callable ETL functions**
* Stores **declarative pipeline definitions** (`dict[str, Any]`)
* Groups items by purpose (e.g. `extract`, `transform`, `load`, `pipelines`)
* Contains no execution logic
* Can optionally expose its functions as step templates

A set is purely an organizational and lookup construct.

---

## 2. FraguaRegistry

The registry is a **resolution layer**.

* Holds multiple `FraguaSet` instances
* Resolves functions by `(set_name, function_name)` at runtime
* Resolves pipeline definitions by name
* Performs no execution or compilation

The registry enables flexible composition without hard-coded dependencies.

---

## 3. FraguaStep

A `FraguaStep` represents a **single declarative execution unit**.

* References a function by `(set, function)`
* Declares execution parameters
* Optionally consumes the output of a previous step
* Stores its result under a logical key (`save_as`)

A step defines **what should happen**, not **how it happens**.

---

## 3.1 FraguaStepBuilder

A `FraguaStepBuilder` is a **mutable builder** used to construct immutable `FraguaStep` objects.

* Provides a fluent configuration API
* Supports method chaining (`with_params`, `with_use`, `with_save_as`)
* Produces immutable steps via `.build()`
* Enables safe and incremental step composition

Builders reduce boilerplate while preserving immutability.

---

## 3.2 FraguaStepIndex

A `FraguaStepIndex` is a **template registry for step builders**.

* Stores `FraguaStepBuilder` templates by name
* Returns fresh builder instances on access
* Is populated automatically from `FraguaSet` definitions
* Is consumed exclusively by macros

This enables reusable step patterns without implicit behavior.

---

## 4. Declarative Pipelines

Pipelines in Fragua are **pure declarative definitions**, represented as dictionaries.

```python
{
    "name": "daily_sales",
    "steps": [
        {"set": "extract", "function": "read_csv"},
        {"set": "transform", "function": "clean_data"},
        {"set": "load", "function": "write_db"},
    ]
}
```

Key characteristics:

* Pipelines are **editable, replaceable, and updateable**
* They contain no runtime state
* They are compiled into `FraguaPipeline` objects only at execution time
* Compilation expands macros and validates dependencies

Runtime pipelines are ephemeral and never persisted.

---

## 5. FraguaPipeline (Runtime Artifact)

A `FraguaPipeline` is a **compiled execution plan**.

* Contains an ordered list of `FraguaStep`
* Is produced from a declarative definition
* Is executed by the agent
* Is discarded after execution

It exists only at runtime.

---

## 6. FraguaAgent

The agent is a **stateless execution primitive**.

* Receives a compiled pipeline
* Resolves functions via the registry
* Executes steps sequentially
* Produces a `FraguaBox` with results

The agent holds no state between runs.

---

## 7. FraguaWarehouse

The warehouse is an **in-memory result store**.

* Stores execution outputs
* Indexed by `save_as`
* Intended for inspection, debugging, and assertions

The warehouse exists only during runtime.

---

## 8. FraguaEnvironment

The environment is the **orchestration boundary** of Fragua.

It owns exactly one:

* `FraguaRegistry`
* `FraguaAgent`
* `FraguaWarehouse`
* `FraguaStepIndex`

It provides high-level APIs to:

* Create and register sets
* Register functions and pipeline definitions
* Automatically index step builders from sets
* Compile declarative pipelines (with macro expansion)
* Execute pipelines from multiple representations
* Update or replace pipeline definitions
* Inspect execution results

The environment enables structure without enforcing it.

---

## Macros and Step Composition

Macros (e.g. `transform_chain`) expand into multiple steps automatically.

* Macros consume **only** `FraguaStepBuilder` templates from the `StepIndex`
* Expansion happens at compile time
* The final macro step may expose a `save_as` key for downstream use

Macros are declarative and deterministic.

---

## Execution Entry Point

Fragua exposes a single execution API:

```python
env.execute_pipeline(pipeline)
```

Supported inputs:

* `FraguaPipeline` → executed directly
* `str` → resolved from registry, compiled, then executed
* `dict` → compiled inline, then executed

This unifies execution flow and removes ambiguity.

---

## Typical Workflow
    
1. Create an environment
2. Define one or more `FraguaSet`
3. Register functions into sets
4. Register declarative pipeline definitions
5. Optionally update or replace pipeline definitions
6. Execute pipelines
7. Inspect results from the warehouse

---

## Design Principles

* **Minimalism** — no feature without a clear purpose
* **Explicitness** — no hidden behavior
* **Single Responsibility** — each component does one thing
* **Declarative First** — definitions before execution
* **Runtime Only** — no persistence, no side effects

---

## What Fragua Is Not

Fragua is not:

* A scheduler
* A workflow orchestrator
* A production ETL engine
* A data platform

Fragua is a **development framework for ETL design, validation, and reasoning**.

---

## Key Features

- **🔧 Declarative Pipeline Definition**: Define ETL pipelines as simple dictionaries
- **⚡ In-Memory Execution**: Fast, stateless execution without external dependencies
- **🏗️ Component-Based Architecture**: Modular design with clear separation of concerns
- **🧪 Development-Focused**: Perfect for testing and validating ETL logic before production
- **🔍 Macro Support**: Automate common patterns with expandable macros
- **📊 Result Inspection**: Built-in result storage for debugging and analysis

## Examples

### Using Transform Chains

```python
# Define a transformation chain with multiple steps
pipeline = {
    "name": "data_cleaning",
    "steps": [
        {"set": "extract", "function": "read_excel", "save_as": "raw_data"},
        {
            "macro": "transform_chain",
            "set": "transform", 
            "step_prefix": "clean",
            "start_from": "raw_data",
            "save_as": "clean_data",
            "steps": [
                {"function": "remove_duplicates"},
                {"function": "fill_missing_values"},
                {"function": "standardize_columns"}
            ]
        },
        {"set": "load", "function": "write_csv", "use": "clean_data"}
    ]
}
```

### Programmatic Pipeline Building

```python
# Build pipelines using the fluent API
pipeline = (
    env.create_pipeline("excel_pipeline")
    .add(extract_step)
    .add(*transform_steps)
    .add(load_step)
    .build()
)
```

## Requirements

- Python 3.10+
- pandas

## License

MIT License
