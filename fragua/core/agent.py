"""Fragua agent.

Defines the minimal execution primitive responsible for
running ETL functions.
"""

from fragua import FraguaRegistry, FraguaWarehouse

from fragua.core.pipeline import FraguaPipeline


class FraguaAgent:
    """
    Stateless execution agent.

    A FraguaAgent executes callables and returns their results.
    It does not resolve functions, store data or manage metadata.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the agent.

        Parameters
        ----------
        name:
            Logical name of the agent.
        """
        self.name = name

    def run_pipeline(
        self,
        pipeline: FraguaPipeline,
        registry: FraguaRegistry,
        warehouse: FraguaWarehouse,
    ) -> None:
        """
        Execute a pipeline step by step.
        """

        for step in pipeline.steps():
            fn = registry.get_function(step.action, step.function)
            if fn is None:
                raise ValueError(f"Function not found: {step.function} ({step.action})")

            if step.use:
                input_data = warehouse.get(step.use)
                result = fn(input_data=input_data, **step.params)
            else:
                result = fn(**step.params)

            key = step.save_as or step.function
            warehouse.store(
                key=key,
                result=result,
                metadata={
                    "action": step.action,
                    "function": step.function,
                    "pipeline": pipeline.name,
                },
            )
