"""Function factory for transform functions."""

from typing import Callable, List, Tuple, Dict, Any, Optional
import pandas as pd

from fragua.core.registry import FraguaRegistry


def transform_function_schema(
    name: str,
    steps: List[Tuple[str, str, Optional[Dict[str, Any]]]],
    registry: FraguaRegistry,
) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """
    Factory to create a composite transformation function.

    Each step definition is a tuple:
        (set_name, function_name, params)

    The resulting function receives a DataFrame and applies
    the registered functions sequentially.
    """

    def transformation(input_data: pd.DataFrame) -> pd.DataFrame:
        result_df = input_data.copy()

        for idx, (set_name, func_name, params) in enumerate(steps):
            function_set = registry.get_set(set_name)
            if function_set is None:
                raise ValueError(
                    f"Registry set not found: '{set_name}' "
                    f"(step {idx + 1} in '{name}')"
                )

            func = function_set.get_function(func_name)
            if func is None:
                raise ValueError(
                    f"Function '{func_name}' not found in set '{set_name}' "
                    f"(step {idx + 1} in '{name}')"
                )

            func_params = params or {}

            try:
                result_df = func(result_df, **func_params)
            except Exception as e:
                raise RuntimeError(
                    f"Error applying step {idx + 1} "
                    f"('{set_name}.{func_name}') in '{name}': {e}"
                ) from e

        return result_df

    transformation.__name__ = name
    return transformation
