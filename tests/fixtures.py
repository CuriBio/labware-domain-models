# -*- coding: utf-8 -*-
from typing import Any
from typing import Dict
import uuid

from labware_domain_models import BarcodedSbsLabware
from labware_domain_models import LabwareDefinition

GENERIC_UUID = uuid.UUID("3d118df7-3cb1-484e-85cd-b06def38bc91")

GENERIC_LABWARE_DEFINITION_KWARGS: Dict[str, Any] = {
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

GENERIC_LABWARE_DEFINITION = LabwareDefinition(**GENERIC_LABWARE_DEFINITION_KWARGS)

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
