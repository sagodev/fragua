"""Example: how to add and use an internal function (transform and load).

Shows:
- register a transform internal function (callable and dict with metadata)
- register a load internal function (with data_arg)
- invoke the transform function as a step in a pipeline
- retrieve and execute a load internal function directly

Takes `create_function.py` as a reference.
"""

# mypy: ignore-errors
# pylint: disable=duplicate-code


from pathlib import Path
import pandas as pd
import fragua as fg


# --- Config (reduced example) ---
BASE_DIR = Path(__file__).parent

env = fg.FraguaEnvironment("env_internal_fn", fg_config=True)

# --- Create an agent (optional to run typical flows) ---
env.create(fg.AGENT, "agent_1")
agent = env.get(fg.AGENT, "agent_1")


# -------------------------
# 1) TRANSFORM INTERNAL FUNCTION
# -------------------------


def remove_negative_numbers(
    data: pd.DataFrame,
    *,
    config: dict | None = None,
) -> pd.DataFrame:
    """Replace negative values with a configurable threshold.

    Config keys:
        - threshold: minimum allowed value (default: 0)
    """
    cfg = config or {}
    threshold = cfg.get("threshold", 0)

    df = data.copy()
    num_cols = df.select_dtypes(include="number").columns

    for col in num_cols:
        df[col] = df[col].clip(lower=threshold)

    return df


# Register the function directly (the name will be `remove_negative_numbers`)
env.add(
    action=fg.TRANSFORM,
    kind=fg.INTERNAL_LOAD_FUNCTION,
    component=remove_negative_numbers,
)

# It's also possible to register using a dict to add metadata and config_keys
env.add(
    action=fg.TRANSFORM,
    kind=fg.INTERNAL_LOAD_FUNCTION,
    component={
        "function": remove_negative_numbers,
        "purpose": "Set negative numbers to a configurable threshold",
        "config_keys": ["threshold"],
    },
    name="remove_neg_threshold",
)


# -------------------------
# 2) USE THE FUNCTION IN A TRANSFORM PIPELINE
# -------------------------

# Example data
test_df = pd.DataFrame({"a": [1, -2, 3], "b": [-1, 5, -6], "c": ["X", "Y", "Z"]})

print("Original:\n", test_df)

# Run pipeline using the registered name
transformed = fg.execute_transform_pipeline(
    input_data=test_df,
    steps=["remove_negative_numbers"],
    config_keys={"threshold": 0},
)

print("Transformado (remove_negative_numbers):\n", transformed)

# Run the pipeline using the registered alias (remove_neg_threshold)
transformed2 = fg.execute_transform_pipeline(
    input_data=test_df,
    steps=["remove_neg_threshold"],
    config_keys={"threshold": 1},
)

print("Transformado (remove_neg_threshold, threshold=1):\n", transformed2)


# -------------------------
# 3) LOAD INTERNAL FUNCTION
# -------------------------


def ensure_id_column(data: pd.DataFrame) -> pd.DataFrame:
    """Ensure that the 'id' column exists in the data and create it if missing."""

    df = data.copy()
    if "id" not in df.columns:
        # for example, create a sequential id
        df.insert(0, "id", range(1, len(df) + 1))
    return df


# Register as a load internal function; indicate that the function receives 'data' via data_arg
env.add(
    action=fg.LOAD,
    kind=fg.INTERNAL_LOAD_FUNCTION,
    component={
        "function": ensure_id_column,
        "purpose": "Ensure 'id' column exists in data",
        "config_keys": [],
        "data_arg": fg.FieldType.DATA.value,
    },
)

# Retrieve the internal function spec and execute it directly
spec = env.get(fg.INTERNAL_LOAD_FUNCTION, "ensure_id_column")
print("Load internal spec:", spec)

df_with_id = spec.func(test_df)
print("Data after ensure_id_column:\n", df_with_id)

# -------------------------
# END
# -------------------------

print("Example completed: internal functions registered and executed.")
