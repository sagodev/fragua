"""Generate an FraguaStep squecuence."""

from typing import List, Dict, Any, Tuple
from fragua.core.step import FraguaStep


def generate_steps_sequence(*steps_def: Tuple[str, Dict[str, Any]]) -> List[FraguaStep]:
    """
    Generate a list of FraguaStep from a sequence of function names and parameters.

    Each step definition is a tuple:
        (function_name, params_dict)

    Args:
        *steps_def: Variable number of tuples defining each step.

    Returns:
        List[fg.FraguaStep]: Steps ready to be added to a pipeline.
    """
    steps = []
    prev_output = None

    for idx, (func_name, params) in enumerate(steps_def):
        # Generate a unique save_as name
        save_as = f"{func_name}_step_{idx+1}"

        # Create the step
        step = FraguaStep(
            function=func_name, params=params, save_as=save_as, use=prev_output
        )

        steps.append(step)
        prev_output = save_as  # the next step will use this as input

    return steps
