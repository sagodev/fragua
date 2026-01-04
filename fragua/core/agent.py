"""Fragua agent.

Stateless execution primitive responsible for running pipelines.
"""

from typing import Callable
import pandas as pd

from fragua.core.pipeline import FraguaPipeline
from fragua.core.registry import FraguaRegistry
from fragua.core.box import FraguaBox
from fragua.core.step import FraguaStep


# pylint: disable=too-few-public-methods


class FraguaAgent:
    """
    Stateless execution agent.

    Executes pipeline steps and returns a FraguaBox containing
    the final result.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    # -------------------- Public API -------------------- #

    def run_pipeline(
        self,
        *,
        pipeline: FraguaPipeline,
        registry: FraguaRegistry,
    ) -> FraguaBox:
        """
        Execute a pipeline and return a FraguaBox containing all step results.
        """
        context, results = self._initialize_execution_state()

        for step in pipeline.steps():
            result = self._execute_step(
                step=step,
                registry=registry,
                context=context,
            )

            key = self._resolve_step_result_key(step)
            context[key] = result
            results[key] = result

        self._validate_execution_results(results)

        return self._build_result_box(
            pipeline=pipeline,
            results=results,
        )

    # -------------------- Execution helpers -------------------- #

    def _initialize_execution_state(
        self,
    ) -> tuple[dict[str, object], dict[str, pd.DataFrame]]:
        """
        Initialize the execution context and results container.
        """
        return {}, {}

    def _execute_step(
        self,
        *,
        step: FraguaStep,
        registry: FraguaRegistry,
        context: dict[str, object],
    ) -> pd.DataFrame:
        """
        Execute a single pipeline step and return its result.
        """
        fn = self._resolve_step_function(
            registry=registry,
            set_name=step.set_name,
            function_name=step.function,
        )

        if step.use:
            input_data = context.get(step.use)
            return fn(input_data=input_data, **step.params)

        return fn(**step.params)

    def _resolve_step_function(
        self,
        *,
        registry: FraguaRegistry,
        set_name: str,
        function_name: str,
    ) -> Callable[..., pd.DataFrame]:
        """
        Resolve a function from a specific registry set.
        """
        function_set = registry.get_set(set_name)
        if function_set is None:
            raise ValueError(f"Registry set not found: {set_name}")

        fn = function_set.get_function(function_name)
        if fn is None:
            raise ValueError(
                f"Function '{function_name}' not found in set '{set_name}'"
            )

        return fn

    def _resolve_step_result_key(self, step: FraguaStep) -> str:
        """
        Determine the storage key for a step result.
        """
        return step.save_as or step.function

    # -------------------- Validation helpers -------------------- #

    def _validate_execution_results(
        self,
        results: dict[str, pd.DataFrame],
    ) -> None:
        """
        Validate that the pipeline produced at least one result.
        """
        if not results:
            raise ValueError("Pipeline produced no results.")

    # -------------------- Result helpers -------------------- #

    def _build_result_box(
        self,
        *,
        pipeline: FraguaPipeline,
        results: dict[str, pd.DataFrame],
    ) -> FraguaBox:
        """
        Build the FraguaBox containing execution results and metadata.
        """
        return FraguaBox(
            key=pipeline.name,
            result=results,
            metadata={
                "agent": self.name,
                "pipeline": pipeline.name,
                "steps": [step.function for step in pipeline.steps()],
            },
        )
