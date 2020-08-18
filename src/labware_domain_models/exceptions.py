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
