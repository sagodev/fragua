"""Fragua Agent Class."""

from __future__ import annotations
from typing import Callable, Dict, Any, List

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
    ) -> FraguaBox:
        """
        Execute a pipeline with explicit inputs.
        """
        inputs = inputs or {}
        working_data: Dict[str, object] = {}

        steps_metadata: List[Dict[str, Any]] = []

        for index, step in enumerate(pipeline.steps(), start=1):
            result = self._execute_step(
                step=step,
                registry=registry,
                inputs=inputs,
                working_data=working_data,
            )

            key = self._resolve_step_result_key(step)
            working_data[key] = result

            step_meta: Dict[str, Any] = {
                "order": index,
                "set": step.set_name,
                "function": step.function,
                "used_input": step.use,
                "produced_key": key,
                "params": step.params,
                "status": "ok",
            }

            # ---- Macro-aware enrichment (PASSIVE) ----
            origin = getattr(step, "origin", None)
            if isinstance(origin, dict):
                step_meta["origin"] = origin

            steps_metadata.append(step_meta)

        self._validate_execution_results(working_data)

        return self._build_result_box(
            pipeline=pipeline,
            results=working_data,
            inputs=inputs,
            steps_metadata=steps_metadata,
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
