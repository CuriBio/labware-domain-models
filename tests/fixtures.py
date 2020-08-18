# -*- coding: utf-8 -*-
import uuid

from labware_domain_models import BarcodedSbsLabware
from labware_domain_models import LabwareDefinition

GENERIC_UUID = uuid.uuid4()

GENERIC_LABWARE_DEFINITION_KWARGS = {
    "name": "12-well",
    "uuid": GENERIC_UUID,
    "row_count": 3,
    "column_count": 4,
    "center_of_a1": (8, 7),
    "plate_height": 13.4,
    "distance_to_liquid": 4,
    "row_center_to_center_spacing": 12,
    "column_center_to_center_spacing": 15,
}

GENERIC_LABWARE_DEFINITION = LabwareDefinition(
    **GENERIC_LABWARE_DEFINITION_KWARGS  # type: ignore
)

GENERIC_LABWARE_DEFINITION_2 = LabwareDefinition(
    name="96-well", uuid=GENERIC_UUID, row_count=3, column_count=4
)

GENERIC_BARCODED_SBS_LABWARE_KWARGS = {
    "uuid": GENERIC_UUID,
    "barcode": "AB9938",
    "labware_definition": GENERIC_LABWARE_DEFINITION_2,
}

GENERIC_BARCODED_SBS_LABWARE = BarcodedSbsLabware(
    uuid=GENERIC_UUID, barcode="AB9938", labware_definition=GENERIC_LABWARE_DEFINITION_2
)
