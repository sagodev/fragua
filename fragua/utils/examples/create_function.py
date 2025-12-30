"""Example of function creation, registration and use."""

# mypy: ignore-errors
# pylint: disable=duplicate-code

from pathlib import Path
import pandas as pd
import fragua as fg


# --- Config ---
BASE_DIR = Path(__file__).parent
INPUT_XLSX = BASE_DIR / "test_files" / "input_files" / "test_data.xlsx"
OUTPUT_XLSX = BASE_DIR / "test_files" / "output_files"


env = fg.FraguaEnvironment("env", fg_config=True)

env.create(fg.EXTRACT, fg.AGENT, "agent_1")

agent = env.get(fg.EXTRACT, fg.AGENT, "agent_1")


# -------------------------
# CREATION OF AN FUNCTION
# -------------------------
def transform_pipeline_func(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """transform pipeline func test."""

    # OPTIONAL: set config keys for internal functions to execute
    config_keys: dict[str, str] = {
        "categorical_fill": "unknown",
        "numerical_fill": "mean",
    }

    # execute transform function pipeline
    return fg.execute_transform_pipeline(
        input_data=data,
        config_keys=config_keys,
        steps=[
            fg.ITF.FILL_MISSING.value,
            fg.ITF.STANDARDIZE.value,
        ],
    )


# -------------------------
# REGISTRATION ON SET
# -------------------------


# do it directly saving the function
env.add(action=fg.TRANSFORM, kind=fg.FUNCTION, component=transform_pipeline_func)


# OR if you want save some metadata; first set function record fields
func_test = {
    # define the action
    fg.FieldType.ACTION.value: fg.ActionType.TRANSFORM.value,
    # define purpose of the function
    fg.FieldType.PURPOSE.value: ("do something great(I guess..)."),
    # reference function
    fg.FieldType.FUNCTION.value: transform_pipeline_func,
}

# and then add function with fields to functions set
env.add(action=fg.TRANSFORM, kind=fg.FUNCTION, component=func_test)


agent.from_excel(save_as="extracted_data", path=str(INPUT_XLSX))

# to use custom function you have to use the 'work' agent function.
agent.work(
    function="transform_pipeline_func",
    apply_to="extracted_data",
    save_as="transformed_data",
)
agent.to_excel(
    apply_to=["extracted_data", "transformed_data"],
    directory=str(OUTPUT_XLSX),
    file_name="output_file",
)
