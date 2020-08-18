# -*- coding: utf-8 -*-
"""Exceptions related to labware."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .labware_definitions import LabwareDefinition


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
        labware_definition: "LabwareDefinition",
    ) -> None:
        super().__init__()
        self.checked_column = checked_column
        self.checked_row = checked_row
        self.labware_definition = labware_definition
