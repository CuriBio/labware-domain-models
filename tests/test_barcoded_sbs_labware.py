# -*- coding: utf-8 -*-
from domain_model import DomainModel
from immutable_data_validation.errors import ValidationCollectionCannotCoerceError
from immutable_data_validation.errors import ValidationCollectionEmptyValueError
from labware_domain_models import BarcodedSbsLabware
import pytest

from .fixtures import GENERIC_BARCODED_SBS_LABWARE_KWARGS
from .fixtures import GENERIC_UUID


def test_BarcodedSbsLabware_autopopulate__fills_uuid():
    m = BarcodedSbsLabware()
    m.autopopulate()
    assert m.uuid is not None


def test_BarcodedSbsLabware_validate_barcode__raises_error_if_not_string():
    m = BarcodedSbsLabware(barcode=23)
    with pytest.raises(ValidationCollectionCannotCoerceError):
        m.validate_barcode()


def test_BarcodedSbsLabware_validate_barcode__raises_error_allow_null_disabled():
    m = BarcodedSbsLabware()
    with pytest.raises(ValidationCollectionEmptyValueError):
        m.validate_barcode(allow_null=False)


def test_BarcodedSbsLabware_validate_does_not_autopopulate_LabwareDefinition_if_flagged(
    mocker,
):
    m = BarcodedSbsLabware(**GENERIC_BARCODED_SBS_LABWARE_KWARGS)

    mocker.spy(m.labware_definition, "autopopulate")
    m.validate(autopopulate=False)
    assert m.labware_definition.autopopulate.call_count == 0


def test_BarcodedSbsLabware_super_is_called_during_init(mocker):
    mocked_init = mocker.patch.object(DomainModel, "__init__")
    BarcodedSbsLabware()
    assert mocked_init.call_count == 1


def test_BarcodedSbsLabware__validate_hash_components_calls_super__and_raises_error_if_invalid_id(
    mocker,
):
    spied_validate = mocker.spy(DomainModel, "validate_hash_components")
    with pytest.raises(ValidationCollectionEmptyValueError) as e:
        BarcodedSbsLabware().validate_hash_components(autopopulate=False)
    assert "uuid" in str(e)
    assert spied_validate.call_count == 1


def test_BarcodedSbsLabware__hash__hashes_uuid():
    m = BarcodedSbsLabware(uuid=GENERIC_UUID)
    assert hash(m) == hash((GENERIC_UUID,))
