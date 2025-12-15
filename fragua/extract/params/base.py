"""Extract Params Class."""

from fragua.core.params import FraguaParams


# pylint: disable=too-few-public-methods


class ExtractParams(FraguaParams):
    """
    Base parameter class for all extraction configurations.

    This class provides the common structure and summary behavior
    shared by all extract parameter schemas. Concrete extraction
    parameter classes should extend this class and define their
    specific fields and descriptions.
    """

    def __init__(self, style: str) -> None:
        """
        Initialize extract parameters for a specific extraction style.

        Args:
            style: Identifier of the extraction style (e.g. "csv",
                "excel", "sql", "api").
        """
        super().__init__(action="extract", style=style)
