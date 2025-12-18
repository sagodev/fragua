"""Actions class."""

from typing import Any, Dict, Optional
from fragua.core.fragua_instance import FraguaInstance
from fragua.core.registry import FraguaRegistry


class FraguaActions(FraguaInstance):
    """Container for all action registries (extract, transform, load)."""

    def __init__(
        self,
        extract: Optional[FraguaRegistry] = None,
        transform: Optional[FraguaRegistry] = None,
        load: Optional[FraguaRegistry] = None,
    ) -> None:
        super().__init__(instance_name="actions")
        self._extract = FraguaRegistry("extract") if extract is None else extract
        self._transform = (
            FraguaRegistry("transform") if transform is None else transform
        )
        self._load = FraguaRegistry("load") if load is None else load

    @property
    def extract(self) -> FraguaRegistry:
        """
        Access the Extract action registry.

        Returns:
            The ExtractRegistry instance.
        """
        return self._extract

    @property
    def transform(self) -> FraguaRegistry:
        """
        Access the Transform action registry.

        Returns:
            The TransformRegistry instance.
        """
        return self._transform

    @property
    def load(self) -> FraguaRegistry:
        """
        Access the Load action registry.

        Returns:
            The LoadRegistry instance.
        """
        return self._load

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of all registered actions.

        This method aggregates the summaries of each action registry
        (extract, transform, and load) into a single structured object.


        Returns:
            Dict([str, Any]):
                A dictionary with the following structure:
                - extract (dict): Summary of the Extract registry
                - transform (dict): Summary of the Transform registry
                - load (dict): Summary of the Load registry
        """
        return {
            "extract": self.extract.summary(),
            "transform": self.transform.summary(),
            "load": self.load.summary(),
        }
