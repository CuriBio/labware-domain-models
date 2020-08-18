# -*- coding: utf-8 -*-
"""Exceptions related to labware."""


class WellCoordinatesGenerationError(Exception):
    pass


class WellCoordinatesRequireA1CenterError(WellCoordinatesGenerationError):
    pass


class WellCoordinatesRequireRowOffsetError(WellCoordinatesGenerationError):

    pass


class WellCoordinatesRequireColumnOffsetError(WellCoordinatesGenerationError):
    pass


class CartesianVectorRequirePlateHeightError(Exception):
    pass


class PositionInvalidForLabwareDefinitionError(Exception):
    """Positions must be within the rows and columns defined for a labware."""

    def __init__(
        self,
        checked_row: int,
        checked_column: int,
        labware_definition: "LabwareDefinition",  # type: ignore # noqa: F821  # Tanner (8/18/20): mypy and flake8 both complain about LabwareDefinition not being defined here even though we put it in quotes
    ) -> None:
        super().__init__()
        self.checked_column = checked_column
        self.checked_row = checked_row
        self.labware_definition = labware_definition
