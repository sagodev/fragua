"""Fragua agent.

Stateless execution primitive responsible for running pipelines.
"""

import pandas as pd
from fragua.core.pipeline import FraguaPipeline
from fragua.core.registry import FraguaRegistry
from fragua.core.box import FraguaBox


class FraguaAgent:
    """
    Stateless execution agent.

    Executes pipeline steps and returns a FraguaBox containing
    the final result.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def run_pipeline(
        self,
        pipeline: FraguaPipeline,
        registry: FraguaRegistry,
    ) -> FraguaBox:
        """
        Execute a pipeline and return a single FraguaBox containing all step results.

        Parameters
        ----------
        pipeline : FraguaPipeline
            Pipeline to execute.
        registry : FraguaRegistry
            Registry to resolve functions.

        Returns
        -------
        FraguaBox
            Single box containing all step results keyed by step.save_as or step.function.
        """
        function_set = registry.get_set("functions")
        if function_set is None:
            raise ValueError("Function registry set not found")

        context: dict[str, object] = {}
        all_results: dict[str, pd.DataFrame] = {}

        for step in pipeline.steps():
            fn = function_set.get_function(step.function)
            if fn is None:
                raise ValueError(f"Function not found: {step.function}")

            if step.use:
                input_data = context.get(step.use)
                result = fn(input_data=input_data, **step.params)
            else:
                result = fn(**step.params)

            key = step.save_as or step.function
            context[key] = result
            all_results[key] = result

        if not all_results:
            raise ValueError("Pipeline produced no results.")

        return FraguaBox(
            key=pipeline.name,
            result=all_results,
            metadata={
                "agent": self.name,
                "pipeline": pipeline.name,
                "steps": [step.function for step in pipeline.steps()],
            },
        )
