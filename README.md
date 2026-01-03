# Fragua

Fragua is a lightweight Python framework designed to **design, test, and validate ETL pipelines and functions** in a controlled, in-memory environment.

It provides a minimal execution model where ETL functions can be registered, composed, executed in sequence, and their intermediate or final results inspected — without schedulers, persistence layers, or external infrastructure.

Fragua is intentionally simple and explicit by design.

---

## Purpose

Fragua exists to answer a small set of focused questions:

> *Does this ETL function behave as expected?*  
> *Does this sequence of ETL steps produce the correct result?*

It is not a workflow orchestrator or a production ETL engine.  
It is a **developer-oriented tool** for modeling, validating, and experimenting with ETL logic.

---

## Core Concepts

Fragua is composed of a small set of orthogonal components.

### 1. FraguaSet

A `FraguaSet` is a **namespace for ETL functions**.

* Stores named callables
* No execution logic
* No awareness of pipelines or data

Typical sets are: `extract`, `transform`, `load`.

---

### 2. FraguaRegistry

The registry is a **function index**.

* Holds multiple `FraguaSet` instances
* Resolves functions by name
* Performs no execution

---

### 3. FraguaAgent

The agent is a **pure executor**.

* Receives a pipeline
* Executes steps sequentially
* Returns execution results

The agent contains no domain logic and no state.

---

### 4. FraguaPipeline

The pipeline represents an **ordered execution plan**.

* Defines a sequence of `FraguaStep`
* Preserves execution order
* Declarative only (no execution logic)

A pipeline is executed by an agent at runtime.

---

### 5. FraguaStep

A step represents a **single unit of execution**.

* References a registered function
* Declares parameters
* Optionally consumes the output of a previous step
* Stores its result under a logical key (`save_as`)

A step describes *what* to execute, not *how*.

---

### 6. FraguaWarehouse

The warehouse is an **in-memory result store**.

* Holds all step outputs
* Indexed by `save_as`
* Intended for inspection, debugging, and assertions

---

### 7. FraguaEnvironment

The environment is the **orchestration boundary**.

It owns:

* One registry
* One agent
* One warehouse

It provides APIs to:

* Register functions and pipelines
* Execute pipelines
* Retrieve results

---

## Helper Abstractions

Fragua includes optional helpers to reduce boilerplate.

### Composite Transform Functions

`transform_fn_schema` allows composing multiple transformation functions into a single reusable transform:

```python
basic_transformation = fg.transform_fn_schema(
    name="basic_transformation",
    steps=[
        ("standardize", None),
        ("add_derived_columns", None),
    ],
    registry=env.registry,
)
```

This enables declarative, reusable transformation logic.

---

### Automatic Step Generation

`generate_steps_sequence` creates a pipeline step sequence from function names:

```python
steps = fg.generate_steps_sequence(
    ("extract_excel", {"path": "input.xlsx"}),
    ("basic_transformation", {}),
    ("load_to_csv", {"path": "output.csv"}),
)
```

---

### Result Inspection

`get_box_dfs_heads` retrieves DataFrame previews from the warehouse with validation:

```python
heads = fg.get_box_dfs_heads(box_result, pipeline.steps())
```

Errors are raised if results are missing or invalid.

---

## Typical Workflow

1. Create an environment
2. Register ETL functions
3. Optionally compose transformations
4. Build a pipeline (manually or automatically)
5. Execute the pipeline
6. Inspect results from the warehouse

---

## Design Principles

Fragua follows these principles:

* **Minimalism** — no feature without purpose
* **Explicitness** — no hidden magic
* **Single Responsibility** — each component does one thing
* **Runtime-only** — no persistence or side effects

---

## What Fragua Is Not

Fragua is not:

* A scheduler
* A workflow orchestrator
* A production ETL engine
* A data platform

It is a **developer tool** for ETL design and validation.

---

## License

MIT License
