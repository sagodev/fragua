"""Fragua agent.

Stateless execution primitive responsible for running pipelines.
"""

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
        Execute a pipeline and return the final result box.

        Parameters
        ----------
        pipeline : FraguaPipeline
            Pipeline to execute.
        registry : FraguaRegistry
            Registry to resolve functions.
        """
        function_set = registry.get_set("functions")
        if function_set is None:
            raise ValueError("Function registry set not found")

        context: dict[str, object] = {}
        last_key: str | None = None
        result: object | None = None

        for step in pipeline.steps():
            fn = function_set.get_function(step.function)
            if fn is None:
                raise ValueError(f"Function not found: {step.function}")

            if step.use:
                input_data = context.get(step.use)
                result = fn(input_data=input_data, **step.params)
            else:
                result = fn(**step.params)

            last_key = step.save_as or step.function
            context[last_key] = result

        if last_key is None:
            raise ValueError("Pipeline produced no result")

        return FraguaBox(
            key=last_key,
            result=result,
            metadata={
                "pipeline": pipeline.name,
                "agent": self.name,
            },
        )
