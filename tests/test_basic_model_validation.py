# -*- coding: utf-8 -*-
import copy
import uuid

from domain_model import DomainModel
from domain_model import InvalidDomainModelSubclassError
from domain_model import ObjectIsNullError
from immutable_data_validation.errors import ValidationCollectionCannotCoerceError
from immutable_data_validation.errors import ValidationCollectionEmptyValueError
from immutable_data_validation.errors import ValidationCollectionMaximumLengthError
from immutable_data_validation.errors import ValidationCollectionMaximumValueError
from immutable_data_validation.errors import ValidationCollectionMinimumLengthError
from immutable_data_validation.errors import ValidationCollectionMinimumValueError
from immutable_data_validation.errors import ValidationCollectionNotAnIntegerError
from labware_domain_models import BarcodedSbsLabware
from labware_domain_models import LabwareDefinition
from misc_test_utils import copy_dict_with_key_removed
from misc_test_utils import domain_model_validate_internals_test
import pytest

from .fixtures import GENERIC_BARCODED_SBS_LABWARE
from .fixtures import GENERIC_BARCODED_SBS_LABWARE_KWARGS
from .fixtures import GENERIC_LABWARE_DEFINITION_KWARGS
from .fixtures import GENERIC_UUID


@pytest.mark.parametrize(
    "model,attribute_under_test,test_value,additional_kwargs,expected_error,expected_texts_in_error,test_description",
    [
        (
            LabwareDefinition,
            None,
            None,
            GENERIC_LABWARE_DEFINITION_KWARGS,
            None,
            None,
            "the generic labware definition validates",
        ),
        (
            LabwareDefinition,
            "uuid",
            None,
            copy_dict_with_key_removed(GENERIC_LABWARE_DEFINITION_KWARGS, "uuid"),
            ValidationCollectionEmptyValueError,
            "uuid",
            "null value not allowed",
        ),
        (
            LabwareDefinition,
            "uuid",
            "not_a_uuid",
            copy_dict_with_key_removed(GENERIC_LABWARE_DEFINITION_KWARGS, "uuid"),
            ValidationCollectionCannotCoerceError,
            "uuid",
            "is not a UUID",
        ),
        (
            LabwareDefinition,
            "name",
            99.3,
            copy_dict_with_key_removed(GENERIC_LABWARE_DEFINITION_KWARGS, "name"),
            ValidationCollectionCannotCoerceError,
            "name",
            "not a string",
        ),
        (
            LabwareDefinition,
            "name",
            None,
            copy_dict_with_key_removed(GENERIC_LABWARE_DEFINITION_KWARGS, "name"),
            ValidationCollectionEmptyValueError,
            "name",
            "null value",
        ),
        (
            LabwareDefinition,
            "name",
            "e" * 256,
            copy_dict_with_key_removed(GENERIC_LABWARE_DEFINITION_KWARGS, "name"),
            ValidationCollectionMaximumLengthError,
            "name",
            "too long",
        ),
        (
            LabwareDefinition,
            "row_count",
            9.2,
            copy_dict_with_key_removed(GENERIC_LABWARE_DEFINITION_KWARGS, "row_count"),
            ValidationCollectionNotAnIntegerError,
            "row_count",
            "not an int",
        ),
        (
            LabwareDefinition,
            "row_count",
            None,
            copy_dict_with_key_removed(GENERIC_LABWARE_DEFINITION_KWARGS, "row_count"),
            ValidationCollectionEmptyValueError,
            "row_count",
            "null value",
        ),
        (
            LabwareDefinition,
            "row_count",
            0,
            copy_dict_with_key_removed(GENERIC_LABWARE_DEFINITION_KWARGS, "row_count"),
            ValidationCollectionMinimumValueError,
            "row_count",
            "too low",
        ),
        (
            LabwareDefinition,
            "row_count",
            33,
            copy_dict_with_key_removed(GENERIC_LABWARE_DEFINITION_KWARGS, "row_count"),
            ValidationCollectionMaximumValueError,
            "row_count",
            "too high",
        ),
        (
            LabwareDefinition,
            "column_count",
            4.2,
            copy_dict_with_key_removed(
                GENERIC_LABWARE_DEFINITION_KWARGS, "column_count"
            ),
            ValidationCollectionNotAnIntegerError,
            "column_count",
            "not an int",
        ),
        (
            LabwareDefinition,
            "column_count",
            None,
            copy_dict_with_key_removed(
                GENERIC_LABWARE_DEFINITION_KWARGS, "column_count"
            ),
            ValidationCollectionEmptyValueError,
            "column_count",
            "null value",
        ),
        (
            LabwareDefinition,
            "column_count",
            0,
            copy_dict_with_key_removed(
                GENERIC_LABWARE_DEFINITION_KWARGS, "column_count"
            ),
            ValidationCollectionMinimumValueError,
            "column_count",
            "too low",
        ),
        (
            LabwareDefinition,
            "column_count",
            49,
            copy_dict_with_key_removed(
                GENERIC_LABWARE_DEFINITION_KWARGS, "column_count"
            ),
            ValidationCollectionMaximumValueError,
            "column_count",
            "too high",
        ),
        (
            BarcodedSbsLabware,
            None,
            None,
            GENERIC_BARCODED_SBS_LABWARE_KWARGS,
            None,
            None,
            "the generic definition validates",
        ),
        (
            BarcodedSbsLabware,
            "uuid",
            "not_a_uuid",
            copy_dict_with_key_removed(GENERIC_BARCODED_SBS_LABWARE_KWARGS, "uuid"),
            ValidationCollectionCannotCoerceError,
            "uuid",
            "not a UUID",
        ),
        (
            BarcodedSbsLabware,
            "uuid",
            None,
            copy_dict_with_key_removed(GENERIC_BARCODED_SBS_LABWARE_KWARGS, "uuid"),
            ValidationCollectionEmptyValueError,
            "uuid",
            "null value",
        ),
        (
            BarcodedSbsLabware,
            "labware_definition",
            DomainModel(),
            copy_dict_with_key_removed(
                GENERIC_BARCODED_SBS_LABWARE_KWARGS, "labware_definition"
            ),
            InvalidDomainModelSubclassError,
            "labware_definition",
            "not a LabwareDefinition",
        ),
        (
            BarcodedSbsLabware,
            "labware_definition",
            None,
            copy_dict_with_key_removed(
                GENERIC_BARCODED_SBS_LABWARE_KWARGS, "labware_definition"
            ),
            ObjectIsNullError,
            "labware_definition",
            "not a LabwareDefinition",
        ),
        (
            BarcodedSbsLabware,
            "barcode",
            21.6,
            copy_dict_with_key_removed(GENERIC_BARCODED_SBS_LABWARE_KWARGS, "barcode"),
            ValidationCollectionCannotCoerceError,
            "barcode",
            "not a string",
        ),
        (
            BarcodedSbsLabware,
            "barcode",
            None,
            copy_dict_with_key_removed(GENERIC_BARCODED_SBS_LABWARE_KWARGS, "barcode"),
            None,
            None,
            "allows null",
        ),
        (
            BarcodedSbsLabware,
            "barcode",
            "f" * 256,
            copy_dict_with_key_removed(GENERIC_BARCODED_SBS_LABWARE_KWARGS, "barcode"),
            ValidationCollectionMaximumLengthError,
            "barcode",
            "too long",
        ),
        (
            BarcodedSbsLabware,
            "barcode",
            "f123",
            copy_dict_with_key_removed(GENERIC_BARCODED_SBS_LABWARE_KWARGS, "barcode"),
            ValidationCollectionMinimumLengthError,
            "barcode",
            "too short",
        ),
    ],
)
def test_model_validate(
    model,
    attribute_under_test,
    test_value,
    additional_kwargs,
    expected_error,
    expected_texts_in_error,
    test_description,
):
    domain_model_validate_internals_test(
        model,
        attribute_under_test,
        test_value,
        additional_kwargs,
        expected_error,
        expected_texts_in_error,
    )


@pytest.mark.parametrize(
    "model1,model2,expected,test_description",
    [
        (
            LabwareDefinition(row_count=8, column_count=12),
            LabwareDefinition(),
            False,
            "empty vs something",
        ),
        (
            LabwareDefinition(
                row_count=8, column_count=12, name="cool plate", uuid=GENERIC_UUID
            ),
            LabwareDefinition(
                row_count=8, column_count=12, name="cool plate", uuid=GENERIC_UUID
            ),
            True,
            "same everything",
        ),
        (LabwareDefinition(row_count=8, column_count=12), 9, False, "different types"),
        (
            LabwareDefinition(row_count=8),
            LabwareDefinition(row_count=5),
            False,
            "different row",
        ),
        (
            LabwareDefinition(name="bob"),
            LabwareDefinition(name="joe"),
            False,
            "different name",
        ),
        (
            LabwareDefinition(uuid=uuid.uuid4()),
            LabwareDefinition(uuid=uuid.uuid4()),
            False,
            "different uuid",
        ),
        (
            LabwareDefinition(center_of_a1=(22, 33.3)),
            LabwareDefinition(center_of_a1=(22, 33.4)),
            False,
            "different xy coordinates of a1",
        ),
        (
            LabwareDefinition(plate_height=12.22),
            LabwareDefinition(plate_height=13.22),
            False,
            "different plate height",
        ),
        (
            LabwareDefinition(row_center_to_center_spacing=9),
            LabwareDefinition(row_center_to_center_spacing=4.5),
            False,
            "different row_center_to_center_spacing",
        ),
        (
            LabwareDefinition(column_center_to_center_spacing=9),
            LabwareDefinition(column_center_to_center_spacing=4.5),
            False,
            "different column_center_to_center_spacing",
        ),
        (
            LabwareDefinition(distance_to_liquid=9),
            LabwareDefinition(distance_to_liquid=4.5),
            False,
            "different distance_to_liquid",
        ),
        (
            GENERIC_BARCODED_SBS_LABWARE,
            copy.deepcopy(GENERIC_BARCODED_SBS_LABWARE),
            True,
            "same everything",
        ),
        (BarcodedSbsLabware(), "wakka", False, "different types"),
        (
            BarcodedSbsLabware(barcode="C1234"),
            BarcodedSbsLabware(barcode="X999"),
            False,
            "different barcode",
        ),
        (
            BarcodedSbsLabware(uuid=uuid.uuid4()),
            BarcodedSbsLabware(uuid=uuid.uuid4()),
            False,
            "different uuid",
        ),
        (
            BarcodedSbsLabware(labware_definition=LabwareDefinition(name="bob")),
            BarcodedSbsLabware(labware_definition=LabwareDefinition(name="joe")),
            False,
            "different LabwareDefinition",
        ),
    ],
)
def test_domain_model__eq__(model1, model2, expected, test_description):
    actual = model1 == model2
    assert actual == expected
