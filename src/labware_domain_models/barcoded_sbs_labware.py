# -*- coding: utf-8 -*-
"""Model for a physical barcoded piece of SBS labware."""
from typing import Optional
from uuid import UUID

from domain_model import DomainModelWithUuid
from domain_model import validate_domain_model
from immutable_data_validation import validate_str

from .labware_definitions import LabwareDefinition


class BarcodedSbsLabware(DomainModelWithUuid):
    """A physical object that has been barcoded."""

    def __init__(
        self,
        uuid: Optional[UUID] = None,
        labware_definition: Optional[LabwareDefinition] = None,
        barcode: Optional[str] = None,
    ):
        super().__init__(uuid=uuid)
        self.labware_definition = labware_definition
        self.barcode = barcode

    def validate_internals(self, autopopulate: bool = True) -> None:
        super().validate_internals(autopopulate=autopopulate)
        validate_domain_model(
            self.labware_definition,
            extra_error_msg="labware_definition",
            instance_of=LabwareDefinition,
            autopopulate=autopopulate,
        )
        self.validate_barcode()

    def validate_barcode(self, allow_null: bool = True) -> None:
        self.barcode = validate_str(
            self.barcode,
            extra_error_msg="barcode",
            allow_null=allow_null,
            maximum_length=255,
            minimum_length=5,
        )

    def __eq__(self, other: object) -> bool:
        if self.__class__ != other.__class__:
            return False
        if not isinstance(other, BarcodedSbsLabware):
            raise NotImplementedError(
                "'other' object should always be of type BarcodedSbsLabware here."
            )

        if self.barcode != other.barcode:
            return False
        if self.uuid != other.uuid:
            return False
        if self.labware_definition != other.labware_definition:
            return False

        return True

    def __hash__(self) -> int:  # pylint: disable=useless-super-delegation
        # pylint is wrong. you MUST define the __hash__ function in every class.
        return int(super().__hash__())
