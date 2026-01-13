"""Fragua Agent Class."""

from __future__ import annotations
from typing import Callable, Dict, Any, List

from fragua.builders.metadata_builder import MetadataBuilder
from fragua.core.pipeline import FraguaPipeline
from fragua.core.registry import FraguaRegistry
from fragua.core.box import FraguaBox
from fragua.core.step import FraguaStep

# pylint: disable=too-few-public-methods


class FraguaAgent:
    """
    Stateless execution agent.

    Executes pipeline steps in-memory and returns a FraguaBox.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    # -------------------- Public API -------------------- #
    def run_pipeline(
        self,
        *,
        pipeline: FraguaPipeline,
        registry: FraguaRegistry,
        inputs: Dict[str, Any] | None = None,
        metadata_builder: MetadataBuilder | None = None,
    ) -> FraguaBox:
        """
        Execute a pipeline with explicit inputs, using MetadataBuilder
        to collect execution metadata.
        """
        inputs = inputs or {}
        working_data: Dict[str, object] = {}

        # Initialize metadata builder if not provided
        if metadata_builder is None:
            metadata_builder = MetadataBuilder(
                environment=self.name,
                agent_name=self.name,
                pipeline_name=pipeline.name,
            )

        for index, step in enumerate(pipeline.steps(), start=1):
            # Execute the step
            result = self._execute_step(
                step=step,
                registry=registry,
                inputs=inputs,
                working_data=working_data,
            )

            # Determine the storage key
            key = self._resolve_step_result_key(step)
            working_data[key] = result

            # Register step in metadata builder
            metadata_builder.add_step(
                order=index,
                step=step,
                produced_key=key,
                status="ok",
            )

        # Validate that at least one result was generated
        self._validate_execution_results(working_data)

        # Get the final step key for metadata finalization
        final_step_key = self._resolve_step_result_key(pipeline.steps()[-1])

        # Finalize metadata and create FraguaBox with inputs and final result
        box_result: Dict[str, object] = {"result": working_data[final_step_key]}
        for k, v in inputs.items():
            box_result[f"input::{k}"] = v

        return FraguaBox(
            key=pipeline.name,
            result=box_result,
            metadata=metadata_builder.finalize(final_step_key=final_step_key),
        )

    # -------------------- Execution helpers -------------------- #

    def _execute_step(
        self,
        *,
        step: FraguaStep,
        registry: FraguaRegistry,
        inputs: Dict[str, Any],
        working_data: Dict[str, object],
    ) -> object:
        """
        Execute a single pipeline step.
        """
        fn = self._resolve_step_function(
            registry=registry,
            set_name=step.set_name,
            function_name=step.function,
        )

        if step.use:
            if step.use in working_data:
                value = working_data[step.use]
            elif step.use in inputs:
                value = inputs[step.use]
            else:
                raise ValueError(
                    f"Step '{step.function}' expected input from '{step.use}', but it was not found"
                )

            return fn(df=value, **step.params)

        return fn(**step.params)

    def _resolve_step_function(
        self,
        *,
        registry: FraguaRegistry,
        set_name: str,
        function_name: str,
    ) -> Callable[..., object]:
        """
        Resolve a function from a registry set.
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
        results: Dict[str, object],
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
        results: Dict[str, object],
        inputs: Dict[str, Any],
        steps_metadata: List[Dict[str, Any]],
    ) -> FraguaBox:
        """
        Build the FraguaBox containing only input and final result,
        plus agent-level execution metadata.
        """
        last_step = pipeline.steps()[-1]
        final_key = last_step.save_as or last_step.function

        if final_key not in results:
            raise RuntimeError("Final step result not found in execution results")

        box_result: Dict[str, object] = {}

        # Store original inputs
        for key, value in inputs.items():
            box_result[f"input::{key}"] = value

        # Store final output only
        box_result["result"] = results[final_key]

        # Normalize steps metadata
        steps_block: Dict[str, Any] = {
            "total": len(steps_metadata),
            "items": steps_metadata,
        }

        return FraguaBox(
            key=pipeline.name,
            result=box_result,
            metadata={
                "agent": {
                    "name": self.name,
                    "executed_steps": len(steps_metadata),
                },
                "pipeline": {
                    "name": pipeline.name,
                    "final_step": final_key,
                },
                "steps": steps_block,
            },
        )
