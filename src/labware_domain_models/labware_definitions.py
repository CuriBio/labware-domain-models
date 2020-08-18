# -*- coding: utf-8 -*-
"""Objects and functions related to sizes and naming of labware.

Includes things such as column and well coordinates as well as
converting names.
"""
import math
from typing import NamedTuple
from typing import Optional
from typing import Tuple
from typing import Union
from uuid import UUID

from domain_model import DomainModelWithUuid
from immutable_data_validation import validate_int
from immutable_data_validation import validate_str

from .exceptions import CartesianVectorRequirePlateHeightError
from .exceptions import PositionInvalidForLabwareDefinitionError
from .exceptions import WellCoordinatesRequireA1CenterError
from .exceptions import WellCoordinatesRequireColumnOffsetError
from .exceptions import WellCoordinatesRequireRowOffsetError


class CoordinateSystem(NamedTuple):
    """Assumes coordinate system is right-handed."""

    x_of_plate_origin: Union[float, int]
    y_of_plate_origin: Union[float, int]
    z_of_plate_origin: Union[float, int]
    z_points_up: bool


class CartesianVector(NamedTuple):
    x: Union[float, int]  # pylint: disable=invalid-name
    y: Union[float, int]  # pylint: disable=invalid-name
    z: Union[float, int]  # pylint: disable=invalid-name


class WellCoordinate(NamedTuple):
    x: Union[float, int]  # pylint: disable=invalid-name
    y: Union[float, int]  # pylint: disable=invalid-name


def get_row_and_column_from_well_name(well_name: str) -> Tuple[int, int]:
    row_char = well_name[0]
    column = int(well_name[1:]) - 1
    row = ord(row_char) - 65
    return row, column


class LabwareDefinition(DomainModelWithUuid):
    """An abstract definition of a piece of labware.

    Traditionally, all measurements are in millimeters.
    The coordinate system starts at the top left edge of the plate at the
    bottom surface (0, 0, 0) (near A1). Y increases moving down the rows.

    Args:
        uuid: a UUID
        name: a descriptive written name
        row_count: how many rows
        column_count: how many columns
        center_of_a1: x and y coordinates
        plate_height: not including the lid
        row_center_to_center_spacing: e.g. 9 mm for 96-well plate
        column_center_to_center_spacing: e.g. 9 mm for 96-well plate
        distance_to_liquid: from z=0 (i.e. the deck) up including the thickness
            of plate bottom and any space between bottom and deck
    """

    def __init__(
        self,
        uuid: Optional[UUID] = None,
        name: Optional[str] = None,
        row_count: Optional[int] = None,
        column_count: Optional[int] = None,
        center_of_a1: Optional[Tuple[Union[float, int], Union[float, int]]] = None,
        plate_height: Union[float, int] = None,
        row_center_to_center_spacing: Union[float, int] = None,
        column_center_to_center_spacing: Union[float, int] = None,
        distance_to_liquid: Union[float, int] = None,
    ):
        super().__init__(uuid=uuid)
        self.name = name
        self.row_count = row_count
        self.column_count = column_count
        self.center_of_a1 = center_of_a1
        self.plate_height = plate_height
        self.row_center_to_center_spacing = row_center_to_center_spacing
        self.column_center_to_center_spacing = column_center_to_center_spacing
        self.distance_to_liquid = distance_to_liquid

    def validate_internals(self, autopopulate: bool = True) -> None:
        super().validate_internals(autopopulate=autopopulate)
        self.name = validate_str(self.name, extra_error_msg="name", maximum_length=255)
        self.validate_row_and_column_counts()

    def validate_row_and_column_counts(self) -> None:
        # a 1536 well plate is 32x48, so nothing should be larger than that
        self.row_count = validate_int(
            self.row_count, extra_error_msg="row_count", minimum=1, maximum=32
        )
        self.column_count = validate_int(
            self.column_count, extra_error_msg="column_count", minimum=1, maximum=48
        )

    def validate_position(self, test_row: int, test_column: int) -> None:
        """Validate if this row and column exist in this definition."""
        self.validate_row_and_column_counts()  # ensure that the definition is valid before validating against it
        if self.column_count is None:
            raise NotImplementedError("'column_count' should never be None here")
        if self.row_count is None:
            raise NotImplementedError("'row_count' should never be None here")

        raise_error = False
        if test_column >= self.column_count:
            raise_error = True
        if test_row >= self.row_count:
            raise_error = True
        if raise_error:
            raise PositionInvalidForLabwareDefinitionError(test_row, test_column, self)

    def _get_formatted_column_string(self, column: int, pad_zeros: bool) -> str:
        """Format the column to be displayed as a string.

        Args:
            column: zero-based
            pad_zeros: if set to true, on dense plates (more than 9 columns), a leading zero will be added for any single digit numbers
        """
        column_str = "%s" % (column + 1)
        if pad_zeros:
            self.validate_row_and_column_counts()
            if self.column_count is None:
                raise NotImplementedError("'column_count' should never be None here")
            if self.column_count > 10:
                column_str = column_str.zfill(2)
        return column_str

    def get_well_name_from_row_and_column(
        self, row: int, column: int, pad_zeros: bool = False
    ) -> str:
        """Get well name.

        Args:
            row: zero-based
            column: zero-based
            pad_zeros: if set to true, on dense plates (more than 9 columns), a leading zero will be added for any single digit numbers
        """
        row_char = chr(65 + row)
        column_str = self._get_formatted_column_string(column, pad_zeros)
        return "%s%s" % (row_char, column_str)

    def get_row_and_column_from_well_index(self, well_idx: int) -> Tuple[int, int]:
        """Get well row and column (zero-based).

        Args:
            well_idx: zero-based

        Returns:
            row index (zero-based), column index (zero-based)
        """
        self.validate_row_and_column_counts()
        if self.column_count is None:
            raise NotImplementedError("'column_count' should never be None here")
        if self.row_count is None:
            raise NotImplementedError("'row_count' should never be None here")

        row_idx = well_idx % self.row_count
        col_idx = math.floor(well_idx / self.row_count)
        return row_idx, col_idx

    def get_well_name_from_well_index(
        self, well_idx: int, pad_zeros: bool = False
    ) -> str:
        """Get well name.

        Args:
            well_idx: zero-based
            pad_zeros: if set to true, on dense plates (more than 9 columns), a leading zero will be added for any single digit numbers
        """
        row_idx, col_idx = self.get_row_and_column_from_well_index(well_idx)

        return self.get_well_name_from_row_and_column(
            row_idx, col_idx, pad_zeros=pad_zeros
        )

    def __eq__(self, other: object) -> bool:
        if self.__class__ != other.__class__:
            return False
        if not isinstance(other, LabwareDefinition):
            raise NotImplementedError(
                "'other' object should always be of type LabwareDefinition here."
            )

        if self.column_count != other.column_count:
            return False
        if self.row_count != other.row_count:
            return False
        if self.name != other.name:
            return False
        if self.uuid != other.uuid:
            return False
        if self.center_of_a1 != other.center_of_a1:
            return False
        if self.plate_height != other.plate_height:
            return False
        if self.row_center_to_center_spacing != other.row_center_to_center_spacing:
            return False
        if (
            self.column_center_to_center_spacing
            != other.column_center_to_center_spacing
        ):
            return False
        if self.distance_to_liquid != other.distance_to_liquid:
            return False
        return True

    def __hash__(self) -> int:  # pylint: disable=useless-super-delegation
        # pylint is wrong. you MUST define the __hash__ function in every class.
        return int(super().__hash__())

    def get_xy_coordinates_of_well(
        self,
        row_idx: int,
        col_idx: int,
        x_offset: Union[float, int] = 0,
        y_offset: Union[float, int] = 0,
    ) -> WellCoordinate:
        """Get x/y coordinate relative to rear left corner.

        The z-axis is pointing down, meaning y gets positive moving from
        row A to row H. X is positive moving from column 1 to column 12.
        """
        if self.center_of_a1 is None:
            raise WellCoordinatesRequireA1CenterError()
        x_coord, y_coord = self.center_of_a1
        if row_idx > 0:
            if self.row_center_to_center_spacing is None:
                raise WellCoordinatesRequireRowOffsetError()
            y_coord += self.row_center_to_center_spacing * row_idx
        if col_idx > 0:
            if self.column_center_to_center_spacing is None:
                raise WellCoordinatesRequireColumnOffsetError()
            x_coord += self.column_center_to_center_spacing * col_idx
        x_coord += x_offset
        y_coord += y_offset
        return WellCoordinate(x=x_coord, y=y_coord)

    def get_cartesian_vector_to_top_of_well(
        self,
        row_idx: int,
        col_idx: int,
        coordinate_system: CoordinateSystem,
        offset_towards_right_plate_edge: Union[float, int] = 0,
        offset_towards_rear_of_plate: Union[float, int] = 0,
        offset_towards_lid_of_plate: Union[float, int] = 0,
    ) -> CartesianVector:
        """Get coordinate of top of well.

        The coordinate system can be defined as either with z pointing
        up or down, but the kwargs to this function are written as if z
        is pointing up.

        Returns:
            A cartesian vector relative to origin of coordinate system.
        """
        if self.plate_height is None:
            raise CartesianVectorRequirePlateHeightError()
        z_points_up = coordinate_system.z_points_up

        y_offset = offset_towards_rear_of_plate
        y_offset *= -1

        well_coordinate = self.get_xy_coordinates_of_well(
            row_idx,
            col_idx,
            x_offset=offset_towards_right_plate_edge,
            y_offset=y_offset,
        )

        y_transform = -1 if z_points_up else 1
        z_transform = 1 if z_points_up else -1

        x_coord = well_coordinate.x
        y_coord = well_coordinate.y
        y_coord *= y_transform

        z_coord = self.plate_height + offset_towards_lid_of_plate
        z_coord *= z_transform

        # translate onto the offset of the plate orgin from the coordinate origin
        x_coord += coordinate_system.x_of_plate_origin
        y_coord += coordinate_system.y_of_plate_origin
        z_coord += coordinate_system.z_of_plate_origin

        return CartesianVector(x=x_coord, y=y_coord, z=z_coord)

    def create_portrait_definition(self) -> "LabwareDefinition":
        """Create a portrait version of this labware.

        Rotate it 90 degrees clockwise. In the returned definition,
        accessing 'A1' will still be in rear left (so where H1 would be
        in a 96-well plate after rotation). But this creates a
        definition with row and column all swapped to become portrait.
        """
        portrait: "LabwareDefinition" = self.__class__(
            row_count=self.column_count,
            column_count=self.row_count,
            plate_height=self.plate_height,
            distance_to_liquid=self.distance_to_liquid,
            row_center_to_center_spacing=self.column_center_to_center_spacing,
            column_center_to_center_spacing=self.row_center_to_center_spacing,
        )
        if self.center_of_a1 is not None:
            portrait.center_of_a1 = (self.center_of_a1[1], self.center_of_a1[0])

        return portrait
