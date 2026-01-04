"""Generate a FraguaStep sequence."""

from typing import List, Dict, Any, Tuple
from fragua.core.step import FraguaStep


def generate_steps_sequence(
    *steps_def: Tuple[str, str, Dict[str, Any]]
) -> List[FraguaStep]:
    """
    Generate a list of FraguaStep from a sequence of set names,
    function names and parameters.

    Each step definition is a tuple:
        (set_name, function_name, params_dict)

    Args:
        *steps_def:
            Variable number of tuples defining each step.

    Returns:
        List[FraguaStep]: Steps ready to be added to a pipeline.
    """
    steps: List[FraguaStep] = []
    prev_output: str | None = None

    for idx, (set_name, func_name, params) in enumerate(steps_def):
        save_as = f"{func_name}_step_{idx + 1}"

        step = FraguaStep(
            set_name=set_name,
            function=func_name,
            params=params,
            save_as=save_as,
            use=prev_output,
        )

        steps.append(step)
        prev_output = save_as

    return steps
