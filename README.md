# Fragua

Fragua is a lightweight and modular library designed to build ETL/ELT
pipelines and data processing workflows in Python. It provides reusable
components such as environments, agents, styles, parameters, and
storages to orchestrate data extraction, transformation, and loading
with traceability and best practices.

------------------------------------------------------------------------

## What is Fragua?

Fragua provides an abstraction layer for data integration tasks based on
three main agents:

- **Extractor**: retrieves data from different sources such as Excel,
  CSV, or APIs.
- **Transformer**: transforms or enriches data by applying rules or
  models.
- **Loader**: saves or delivers results to final destinations such as
  files or databases.

In addition to the agents, Fragua introduces the concept of **Environments**, 
which act as isolated workspaces that organize and group all components 
involved in a pipeline. An `Environment` manages:

- Registered agents and their lifecycle.
- Registries for `styles`, `functions`, and `params`.
- A dedicated **Warehouse** for storing intermediate or final artifacts.
- Execution settings, logging configuration, and context boundaries.

This design allows you to run multiple pipelines independently, each with 
its own configuration, state, and stored data.

Fragua also includes a storage system with:

- **Warehouse** and **WarehouseManager** to store intermediate artifacts 
  with metadata and traceability.
- A modular architecture where `styles`, `functions`, and `params` can 
  be registered within an `Environment`.

------------------------------------------------------------------------

## Key Features

-   Environment modeling (`Environment`) to isolate and organize working
    instances.
-   Agents (`Extractor`, `Transformer`, `Loader`) with a common
    pipeline, `undo` capability, and operation logging.
-   Registries for `params`, `functions`, and `styles`.
-   Storage types (`Storage`, `Box`, `Container`) and a centralized
    `Warehouse`.
-   Built-in utilities for logging, metrics, and execution state
    summaries.

------------------------------------------------------------------------

## Project Structure

    fragua/
    ├── agents/
    ├── environments/
    ├── functions/
    ├── params/
    ├── styles/
    ├── storages/
    ├── utils/
    └── __init__.py

------------------------------------------------------------------------

## Installation

Install Fragua in editable mode from the root of the repository:

``` bash
python -m pip install -e .
```

Check `requirements.txt` for additional dependencies.

------------------------------------------------------------------------

## Usage Example

``` python
import fragua as fg
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_XLSX = BASE_DIR / "test_files" / "input_files" / "test_data.xlsx"
OUTPUT_XLSX = BASE_DIR / "test_files" / "output_files"

env = fg.create_fragua("fragua_1", "minimal", True)
env.create_extractor("extractor")
env.create_transformer("transformer")
env.create_loader("loader")

extractor = env.get_agent("extractor")
transformer = env.get_agent("transformer")
loader = env.get_agent("loader")

extractor.work(
    "excel",
    save_as="extracted_data",
    path="./test_files/input_files/test_data.xlsx",
    sheet_name=0,
)

transformer.work(
    style="report",
    apply_to="extracted_data",
    save_as="transformed_data",
)

loader.work(
    style="excel",
    apply_to=["extracted_data", "transformed_data"],
    destination="./test_files/output_files",
    file_name="output_file",
)
```

------------------------------------------------------------------------

## Author

**Santiago Lanz**\
📍 Developer and creator of Fragua\
🌐 Portfolio: https://sagodev.github.io/Portfolio-Web-Santiago-Lanz/\
💼 LinkedIn: https://www.linkedin.com/in/santiagolanz/\
🐙 GitHub: https://github.com/SagoDev

------------------------------------------------------------------------

## ⚖️ License

This project is distributed under the **MIT** license.\
See the `LICENSE` file for more details.
