"""Get dataframes heads of results in a FraguaBox."""

from typing import Dict, List
import pandas as pd

from fragua.core.step import FraguaStep


def get_box_dfs_heads(
    box: Dict[str, pd.DataFrame], steps: List[FraguaStep], n: int = 5
) -> Dict[str, pd.DataFrame]:
    """
    Retrieve the head of DataFrames from a FraguaBox for the given steps.

    Args:
        box (dict): FraguaBox returned by the environment (env.warehouse.get(pipeline.name)).
        steps (List[fg.FraguaStep]): List of steps to extract data from.
        n (int): Number of rows to return from each DataFrame.

    Returns:
        dict[str, pd.DataFrame]: Dictionary mapping step save_as names to their head DataFrames.

    Raises:
        ValueError: If a step has no save_as or the data is not found in the box.
    """
    heads = {}

    for step in steps:
        step_name = step.save_as
        if not step_name:
            raise ValueError(f"Step has no 'save_as' defined: {step}")

        if step_name not in box:
            raise ValueError(f"No data found for step '{step_name}' in FraguaBox.")

        df = box[step_name]
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"Data for step '{step_name}' is not a DataFrame.")

        heads[step_name] = df.head(n)

    return heads
