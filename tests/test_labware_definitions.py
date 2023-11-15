# -*- coding: utf-8 -*-
from typing import Any
from typing import Dict

from domain_model import DomainModel
from immutable_data_validation.errors import ValidationCollectionCannotCoerceError
from immutable_data_validation.errors import ValidationCollectionEmptyValueError
from labware_domain_models import CartesianVector
from labware_domain_models import CartesianVectorRequirePlateHeightError
from labware_domain_models import CoordinateSystem
from labware_domain_models import get_row_and_column_from_well_name
from labware_domain_models import LabwareDefinition
from labware_domain_models import PositionInvalidForLabwareDefinitionError
from labware_domain_models import row_index0_to_letters
from labware_domain_models import row_letters_to_index0
from labware_domain_models import WellCoordinate
from labware_domain_models import WellCoordinatesRequireA1CenterError
from labware_domain_models import WellCoordinatesRequireColumnOffsetError
from labware_domain_models import WellCoordinatesRequireRowOffsetError
from misc_test_utils import copy_dict_with_key_removed
import pytest
from pytest import param

from .fixtures import GENERIC_LABWARE_DEFINITION_KWARGS
from .fixtures import GENERIC_UUID


def test_LabwareDefinition_autopopulate__fills_uuid():
    m = LabwareDefinition()
    m.autopopulate()
    assert m.uuid is not None


def test_LabwareDefinition_validate_row_and_column_counts__raises_error_if_row_invalid():
    m = LabwareDefinition(row_count="bob", column_count=12)
    with pytest.raises(ValidationCollectionCannotCoerceError):
        m.validate_row_and_column_counts()


def test_LabwareDefinition_validate_row_and_column_counts__raises_error_if_column_invalid():
    m = LabwareDefinition(row_count=2, column_count="joe")
    with pytest.raises(ValidationCollectionCannotCoerceError):
        m.validate_row_and_column_counts()


@pytest.mark.parametrize(
    "row,expected_index0",
    [
        param("A", 0, id="A: first 0-index of any plate"),
        param("Z", 25, id="Z: last single digit 0-index of any plate"),
        param("AA", 26, id="AA: first double digit 0-index of any plate"),
        param("AF", 31, id="AF: last double digit 0-index of 1536 row plate"),
    ],
)
def test_row_letters_to_index0__handles_rows_with_one_or_more_letters(
    row: str, expected_index0: int
) -> None:
    assert row_letters_to_index0(row) == expected_index0


@pytest.mark.parametrize(
    "index0,expected_row",
    [
        param(0, "A", id="A: first 0-index of any plate"),
        param(25, "Z", id="Z: last single digit 0-index of any plate"),
        param(26, "AA", id="AA: first double digit 0-index of any plate"),
        param(31, "AF", id="AF: last double digit 0-index of 1536 row plate"),
    ],
)
def test_row_index0_to_letters__handles_indices_producing_one_or_more_letters(
    index0: int, expected_row: str
) -> None:
    assert row_index0_to_letters(index0) == expected_row


@pytest.mark.parametrize(
    "labware_definition,test_row,test_column,expected_error,test_description",
    [
        (
            LabwareDefinition(row_count=2, column_count=2),
            1,
            2,
            PositionInvalidForLabwareDefinitionError,
            "column too high",
        ),
        (
            LabwareDefinition(row_count=2, column_count=2),
            2,
            1,
            PositionInvalidForLabwareDefinitionError,
            "row too high",
        ),
        (
            LabwareDefinition(row_count=2, column_count=2),
            1,
            1,
            None,
            "just within the boundary-should not raise error",
        ),
    ],
)
def test_LabwareDefinition_validate_position(
    labware_definition, test_row, test_column, expected_error, test_description
):
    if expected_error is not None:
        with pytest.raises(expected_error):
            labware_definition.validate_position(test_row, test_column)
    else:
        labware_definition.validate_position(test_row, test_column)


def test_LabwareDefinition_super_is_called_during_init(mocker):
    spied_init = mocker.spy(DomainModel, "__init__")
    LabwareDefinition()
    assert spied_init.call_count == 1


@pytest.mark.parametrize(
    "labware_definition,test_row,test_column,zero_pad,expected,test_description",
    [
        (
            LabwareDefinition(row_count=8, column_count=12),
            0,
            0,
            False,
            "A1",
            "96 well first well",
        ),
        (
            LabwareDefinition(row_count=8, column_count=12),
            7,
            11,
            False,
            "H12",
            "96 well last well",
        ),
        (
            LabwareDefinition(row_count=8, column_count=12),
            0,
            0,
            True,
            "A01",
            "zero pad uses two digits in 96 well",
        ),
        (
            LabwareDefinition(row_count=16, column_count=24),
            0,
            0,
            True,
            "A01",
            "zero pad uses two digits in 384 well",
        ),
        (
            LabwareDefinition(row_count=3, column_count=4),
            0,
            0,
            True,
            "A1",
            "zero pad uses one digit in 12 well",
        ),
        (
            LabwareDefinition(row_count=32, column_count=48),
            0,
            0,
            True,
            "A01",
            "zero pad uses 2-digits in 1536 well",
        ),
        (
            LabwareDefinition(row_count=32, column_count=48),
            26,
            47,
            True,
            "AA48",
            "first index with 2-character row in 1536 well",
        ),
        (
            LabwareDefinition(row_count=32, column_count=48),
            31,
            47,
            True,
            "AF48",
            "last row index in 1536 well",
        ),
    ],
)
def test_LabwareDefinition__get_well_name_from_row_and_column(
    labware_definition, test_row, test_column, zero_pad, expected, test_description
):
    actual = labware_definition.get_well_name_from_row_and_column(
        test_row, test_column, pad_zeros=zero_pad
    )
    assert actual == expected


@pytest.mark.parametrize(
    "labware_definition,test_row,test_column,expected,test_description",
    [
        (
            LabwareDefinition(row_count=4, column_count=6),
            0,
            0,
            0,
            "first well (index 0) in 24 well plate",
        ),
        (
            LabwareDefinition(row_count=4, column_count=6),
            3,
            5,
            23,
            "last well (index 23) in 24 well plate",
        ),
        (
            LabwareDefinition(row_count=8, column_count=12),
            7,
            11,
            95,
            "last well (index 95) in 96 well plate",
        ),
        (
            LabwareDefinition(row_count=16, column_count=24),
            0,
            23,
            368,
            "first row and last column (index 368) in 384 well",
        ),
        (
            LabwareDefinition(row_count=3, column_count=4),
            2,
            0,
            2,
            "last row and first column (index 2) in 12 well",
        ),
    ],
)
def test_LabwareDefinition__get_well_index_from_row_and_column(
    labware_definition, test_row, test_column, expected, test_description
):
    actual = labware_definition.get_well_index_from_row_and_column(
        test_row, test_column
    )
    assert actual == expected


@pytest.mark.parametrize(
    "labware_definition,test_well_name,expected,test_description",
    [
        (
            LabwareDefinition(row_count=4, column_count=6),
            "A1",
            0,
            "first well (index 0) in 24 well plate",
        ),
        (
            LabwareDefinition(row_count=4, column_count=6),
            "D6",
            23,
            "last well (index 23) in 24 well plate",
        ),
        (
            LabwareDefinition(row_count=8, column_count=12),
            "H12",
            95,
            "last well (index 95) in 96 well plate",
        ),
        (
            LabwareDefinition(row_count=8, column_count=12),
            "A01",
            0,
            "first well (index 0) in 96 well plate",
        ),
        (
            LabwareDefinition(row_count=16, column_count=24),
            "A24",
            368,
            "first row and last column (index 368) in 384 well",
        ),
        (
            LabwareDefinition(row_count=3, column_count=4),
            "C1",
            2,
            "last row and first column (index 2) in 12 well",
        ),
    ],
)
def test_LabwareDefinition__get_well_index_from_well_name(
    labware_definition, test_well_name, expected, test_description
):
    actual = labware_definition.get_well_index_from_well_name(test_well_name)
    assert actual == expected


@pytest.mark.parametrize(
    "test_well_name,expected_row,expected_column,test_description",
    [("A1", 0, 0, "first well"), ("A02", 0, 1, "A2 zero padded")],
)
def test_get_row_and_column_from_well_name(
    test_well_name, expected_row, expected_column, test_description
):
    actual_row, actual_column = get_row_and_column_from_well_name(test_well_name)
    assert (actual_row, actual_column) == (expected_row, expected_column)


@pytest.mark.parametrize(
    """labware_definition,test_idx,zero_pad,expected,test_description""",
    [
        (
            LabwareDefinition(row_count=8, column_count=12),
            0,
            False,
            "A1",
            "96 well first well",
        ),
        (
            LabwareDefinition(row_count=8, column_count=12),
            95,
            False,
            "H12",
            "96 well last well",
        ),
        (
            LabwareDefinition(row_count=8, column_count=12),
            0,
            True,
            "A01",
            "zero pad uses two digits in 96 well",
        ),
        (
            LabwareDefinition(row_count=16, column_count=24),
            0,
            True,
            "A01",
            "zero pad uses two digits in 384 well",
        ),
        (
            LabwareDefinition(row_count=3, column_count=4),
            4,
            False,
            "B2",
            "middle position in 12 well",
        ),
    ],
)
def test_LabwareDefinition__get_well_name_from_well_index(
    labware_definition, test_idx, zero_pad, expected, test_description
):
    actual = labware_definition.get_well_name_from_well_index(
        test_idx, pad_zeros=zero_pad
    )
    assert actual == expected


@pytest.mark.parametrize(
    """labware_definition,test_idx,expected,test_description""",
    [
        (
            LabwareDefinition(row_count=8, column_count=12),
            0,
            (0, 0),
            "96 well first well",
        ),
        (
            LabwareDefinition(row_count=8, column_count=12),
            95,
            (7, 11),
            "96 well last well",
        ),
        (
            LabwareDefinition(row_count=3, column_count=4),
            4,
            (1, 1),
            "middle position in 12 well",
        ),
    ],
)
def test_LabwareDefinition__get_row_and_column_from_well_index(
    labware_definition, test_idx, expected, test_description
):
    actual = labware_definition.get_row_and_column_from_well_index(test_idx)
    assert actual == expected


def test_LabwareDefinition__get_row_and_column_from_well_index__raises_error_if_row_count_not_set():
    labware_definition = LabwareDefinition(column_count=2)
    with pytest.raises(
        ValidationCollectionEmptyValueError, match="was empty row_count"
    ):
        labware_definition.get_row_and_column_from_well_index(0)


def test_LabwareDefinition__validate_hash_components_calls_super__and_raises_error_if_invalid_id(
    mocker,
):
    spied_validate = mocker.spy(DomainModel, "validate_hash_components")
    with pytest.raises(ValidationCollectionEmptyValueError) as e:
        LabwareDefinition().validate_hash_components(autopopulate=False)
    assert "uuid" in str(e)
    assert spied_validate.call_count == 1


def test_LabwareDefinition__hash__hashes_uuid():
    m = LabwareDefinition(uuid=GENERIC_UUID)
    assert hash(m) == hash((GENERIC_UUID,))


@pytest.mark.parametrize(
    "labware_definition_kwargs,row_idx,col_idx,function_call_kwargs,expected_error,test_description",
    [
        (
            copy_dict_with_key_removed(
                GENERIC_LABWARE_DEFINITION_KWARGS, "center_of_a1"
            ),
            0,
            0,
            {},
            WellCoordinatesRequireA1CenterError,
            "no center defined",
        ),
        (
            copy_dict_with_key_removed(
                GENERIC_LABWARE_DEFINITION_KWARGS, "row_center_to_center_spacing"
            ),
            1,
            0,
            {},
            WellCoordinatesRequireRowOffsetError,
            "row index 1 requires spacing",
        ),
        (
            copy_dict_with_key_removed(
                GENERIC_LABWARE_DEFINITION_KWARGS, "row_center_to_center_spacing"
            ),
            0,
            2,
            {},
            None,
            "row index 0 does not require spacing",
        ),
        (
            copy_dict_with_key_removed(
                GENERIC_LABWARE_DEFINITION_KWARGS, "column_center_to_center_spacing"
            ),
            0,
            1,
            {},
            WellCoordinatesRequireColumnOffsetError,
            "col index 1 requires spacing",
        ),
        (
            copy_dict_with_key_removed(
                GENERIC_LABWARE_DEFINITION_KWARGS, "column_center_to_center_spacing"
            ),
            1,
            0,
            {},
            None,
            "col index 0 does not require spacing",
        ),
    ],
)
def test_LabwareDefinition__get_xy_coordinates_of_well__raises_error_if_definitions_missing(
    labware_definition_kwargs,
    row_idx,
    col_idx,
    function_call_kwargs,
    expected_error,
    test_description,
):
    labware_definition = LabwareDefinition(**labware_definition_kwargs)
    if expected_error is not None:
        with pytest.raises(expected_error):
            labware_definition.get_xy_coordinates_of_well(
                row_idx, col_idx, **function_call_kwargs
            )
    else:
        labware_definition.get_xy_coordinates_of_well(
            row_idx, col_idx, **function_call_kwargs
        )


@pytest.mark.parametrize(
    "labware_definition_kwargs,row_idx,col_idx,x_offset,y_offset,expected_coordinates,test_description",
    [
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            0,
            0,
            None,
            None,
            WellCoordinate(8, 7),
            "simple A1",
        ),
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            2,
            0,
            None,
            None,
            WellCoordinate(8, 31),
            "3rd row",
        ),
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            0,
            2,
            None,
            None,
            WellCoordinate(38, 7),
            "3rd column",
        ),
        (
            copy_dict_with_key_removed(
                GENERIC_LABWARE_DEFINITION_KWARGS, "plate_height"
            ),
            0,
            0,
            None,
            None,
            WellCoordinate(8, 7),
            "no plate height",
        ),
        (
            copy_dict_with_key_removed(
                GENERIC_LABWARE_DEFINITION_KWARGS, "distance_to_liquid"
            ),
            0,
            0,
            None,
            None,
            WellCoordinate(8, 7),
            "no distance to liquid",
        ),
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            0,
            0,
            -2,
            None,
            WellCoordinate(6, 7),
            "x offset",
        ),
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            0,
            0,
            None,
            4,
            WellCoordinate(8, 11),
            "y offset",
        ),
    ],
)
def test_LabwareDefinition__get_xy_coordinates_of_well(
    labware_definition_kwargs,
    row_idx,
    col_idx,
    x_offset,
    y_offset,
    expected_coordinates,
    test_description,
):
    labware_definition = LabwareDefinition(**labware_definition_kwargs)
    kwargs: Dict[str, Any] = dict()
    if x_offset is not None:
        kwargs["x_offset"] = x_offset
    if y_offset is not None:
        kwargs["y_offset"] = y_offset
    actual_coordinates = labware_definition.get_xy_coordinates_of_well(
        row_idx, col_idx, **kwargs
    )
    assert actual_coordinates == expected_coordinates


@pytest.mark.parametrize(
    "labware_definition_kwargs,row_idx,col_idx,coordinate_system,function_call_kwargs,expected_coordinates,test_description",
    [
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            0,
            0,
            CoordinateSystem(0, 0, 0, True),
            {},
            CartesianVector(8, -7, 13.4),
            "simple A1 with coordinate system set to plate origin already, coordinate system has z pointing up",
        ),
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            0,
            0,
            CoordinateSystem(0, 0, 0, False),
            {},
            CartesianVector(8, 7, -13.4),
            "simple A1 with coordinate system set to plate origin already, coordinate system has z pointing down",
        ),
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            0,
            0,
            CoordinateSystem(0, 0, 0, True),
            {"offset_towards_right_plate_edge": 5},
            CartesianVector(13, -7, 13.4),
            "offset in the x axis with z pointing up",
        ),
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            0,
            0,
            CoordinateSystem(0, 0, 0, True),
            {"offset_towards_rear_of_plate": 5},
            CartesianVector(8, -2, 13.4),
            "offset in the y axis with z pointing up",
        ),
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            0,
            0,
            CoordinateSystem(0, 0, 0, False),
            {"offset_towards_rear_of_plate": 4},
            CartesianVector(8, 3, -13.4),
            "offset in the y axis with z pointing down",
        ),
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            0,
            0,
            CoordinateSystem(0, 0, 0, True),
            {"offset_towards_lid_of_plate": 2},
            CartesianVector(8, -7, 15.4),
            "offset in the z axis with z pointing up",
        ),
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            0,
            0,
            CoordinateSystem(0, 0, 0, False),
            {"offset_towards_lid_of_plate": -3},
            CartesianVector(8, 7, -10.4),
            "offset in the z axis with z pointing down",
        ),
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            0,
            0,
            CoordinateSystem(100, 200, 50, True),
            {},
            CartesianVector(108, 193, 63.4),
            "A1 with offset coordinate coordinate system, coordinate system has z pointing up",
        ),
        (
            GENERIC_LABWARE_DEFINITION_KWARGS,
            0,
            0,
            CoordinateSystem(100, 200, 50, False),
            {},
            CartesianVector(108, 207, 36.6),
            "A1 with offset coordinate coordinate system, coordinate system has z pointing down",
        ),
    ],
)
def test_LabwareDefinition__get_cartesian_vector_to_top_of_well(
    labware_definition_kwargs,
    row_idx,
    col_idx,
    coordinate_system,
    function_call_kwargs,
    expected_coordinates,
    test_description,
):
    labware_definition = LabwareDefinition(**labware_definition_kwargs)
    actual_coordinates = labware_definition.get_cartesian_vector_to_top_of_well(
        row_idx, col_idx, coordinate_system, **function_call_kwargs
    )
    assert actual_coordinates == expected_coordinates


def test_LabwareDefinition__get_cartesian_vector_to_top_of_well__raises_error_if_no_plate_height():
    labware_definition = LabwareDefinition(
        **copy_dict_with_key_removed(GENERIC_LABWARE_DEFINITION_KWARGS, "plate_height")
    )
    with pytest.raises(CartesianVectorRequirePlateHeightError):
        labware_definition.get_cartesian_vector_to_top_of_well(
            0, 0, CoordinateSystem(0, 0, 0, False)
        )


def test_LabwareDefinition__create_portrait_definition__rotates_standard_96_well():
    expected_plate_height = 14.2
    expected_row_spacing = 9
    expected_column_spacing = 9
    landscape = LabwareDefinition(
        row_count=8,
        column_count=12,
        plate_height=expected_plate_height,
        row_center_to_center_spacing=expected_row_spacing,
        column_center_to_center_spacing=expected_column_spacing,
    )
    portrait = landscape.create_portrait_definition()
    assert portrait.row_count == 12
    assert portrait.column_count == 8
    assert portrait.plate_height == expected_plate_height
    assert portrait.row_center_to_center_spacing == expected_row_spacing
    assert portrait.column_center_to_center_spacing == expected_column_spacing


def test_LabwareDefinition__create_portrait_definition__rotates_agilent_8_row_trough():
    expected_distance_to_liquid = 2
    expected_row_spacing = (
        9.01  # just to make it different than the 9 in the previous test
    )

    landscape = LabwareDefinition(
        row_count=8,
        center_of_a1=(14.29, 11.18),
        distance_to_liquid=expected_distance_to_liquid,
        row_center_to_center_spacing=expected_row_spacing,
    )
    portrait = landscape.create_portrait_definition()
    assert portrait.row_count is None
    assert portrait.column_count == 8
    assert portrait.center_of_a1 == (11.18, 14.29)
    assert portrait.distance_to_liquid == expected_distance_to_liquid
    assert portrait.column_center_to_center_spacing == expected_row_spacing
    assert portrait.row_center_to_center_spacing is None
