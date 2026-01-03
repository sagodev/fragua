"""Function factory for transform functions."""

from typing import Callable, List, Tuple, Dict, Any, Optional
import pandas as pd

from fragua.core.registry import FraguaRegistry


def transform_function_schema(
    name: str,
    steps: List[Tuple[str, Optional[Dict[str, Any]]]],
    registry: FraguaRegistry,
) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """
    Factory to create a composite transformation function.

    Now 'env' is captured automatically, so FraguaStep only passes the DataFrame.
    """

    def transformation(input_data: pd.DataFrame) -> pd.DataFrame:
        result_df = input_data.copy()

        for idx, (func_name, params) in enumerate(steps):
            func = registry.get_function("functions", func_name)
            if func is None:
                raise ValueError(
                    f"Function '{func_name}' is not registered in the environment."
                )

            func_params = params if params is not None else {}

            try:
                result_df = func(result_df, **func_params)
            except Exception as e:
                raise RuntimeError(
                    f"Error applying step {idx+1} ('{func_name}') in '{name}': {e}"
                ) from e

        return result_df

    transformation.__name__ = name
    return transformation
