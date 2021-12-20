import logging

import stix2
from stix2validator import validate_file
from stix2 import parse
from stix2.v21 import Indicator, ObservedData
from stix2patterns.validator import validate as stix_pattern_validate
from stix_shifter.stix_translation import stix_translation

class ParserV21:
    """
    Parser for translating `stix2.v21.Indicator` and `stix2.v21.ObservedData`
    objects to `cbc_sdk.enterprise_edr.IOC_V2`.
    """

    def __init__(self):
        self.STIX_VERSION = "2.1"

    def parse_file(self, file: str) -> None:
        validate = validate_file(file)
        if validate.is_valid:
            with open(file) as fo:
                stix_content = parse(fo, allow_custom=True, version=self.STIX_VERSION)
                if stix_content.objects:
                    self._parse_stix_objects(stix_content)
                else:
                    logging.info("No objects found")
                    return
        else:
            raise ValueError(f"JSON file is not valid or empty: {validate.as_dict()}")

    def parse_feed(self, *args, **kwargs):
        pass

    def _parse_stix_objects(self, stix_content: stix2.Bundle):
        indicators = []
        observables = []
        for stix_obj in stix_content.objects:
            if isinstance(stix_obj, Indicator):
                indicators.append(self._parse_stix_indicator(stix_obj))
            elif isinstance(stix_obj, ObservedData):
                observables.append(self._parse_stix_observable(stix_obj))
            else:
                continue
        logging.info(f"Located: {len(indicators)} Indicators objects.")
        logging.info(f"Located: {len(observables)} ObservedData objects.")

    def _parse_stix_indicator(self, indicator: Indicator):
        valid = stix_pattern_validate(indicator.pattern, stix_version=self.STIX_VERSION)
        if valid:
            translation = stix_translation.StixTranslation()
            response = translation.translate(
                module="cbcloud",
                translate_type="query",
                data_source={},
                data=indicator.pattern,
                options={"stix_2.1": True}
            )


    def _parse_stix_observable(self, observable: ObservedData):
        pass
