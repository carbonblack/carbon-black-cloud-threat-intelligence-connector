import typing

import validators

from stix2patterns.v21.grammars.STIXPatternListener import STIXPatternListener


class IOCPatternParser:
    """
    Parser for STIX Patterns to dict with mapped values and fields.
    """

    def __init__(self, stix_field_type: str, stix_field_value: str):
        self.mappings = {
            "ipv4-addr:value": {"function": self.parse_ipv4, "field": "netconn_ipv4"},
            "ipv6-addr:value": {
                "function": IOCPatternParser.parse_ipv6,
                "field": "netconn_ipv4",
            },
            "file:hashes.'SHA-256'": {
                "function": IOCPatternParser.parse_sha256,
                "field": "process_hash",
            },
            "artifact:hashes.'SHA-256'": {
                "function": IOCPatternParser.parse_sha256,
                "field": "process_hash",
            },
            "file:hashes.'MD5'": {
                "function": IOCPatternParser.parse_md5,
                "field": "process_hash",
            },
            "artifact:hashes.'MD5'": {
                "function": IOCPatternParser.parse_md5,
                "field": "process_hash",
            },
            "url:value": {
                "function": IOCPatternParser.parse_url,
                "field": "netconn_domain",
            },
            "domain-name:value": {
                "function": IOCPatternParser.parse_domain,
                "field": "netconn_domain",
            },
        }
        self.stix_field_type = stix_field_type
        self.stix_field_value = stix_field_value
        self._parser = self._lookup_parser()

    def _lookup_parser(self) -> typing.Union[dict, None]:
        """
        Getting the associated parser and mapping value for
        the provided `stix_field_type`.

        Returns:
            Dictionary containing the `function` and `field` keys which are
            corresponding to the parser function and the mapped field. None
            if the field cannot be mapped.
        """
        try:
            return self.mappings[self.stix_field_type]
        except KeyError:
            return None

    def parse(self) -> typing.Union[dict, None]:
        """
        The main parsing method, it calls the mapped parser.

        Returns:
            Dictionary containing the mapped field and value of the STIX Object.
        """
        if self.is_parsable:
            parsed_value = self._parser["function"](self.stix_field_value)
            if parsed_value:
                return {"field": self._parser["field"], "value": parsed_value}
            return None
        return None

    @property
    def is_parsable(self) -> bool:
        """
        Checks if there is a parser for the given `stix_field_type`.

        Returns:
            True if a parser is found, False if not.
        """
        if self._parser:
            return True
        return False

    @staticmethod
    def parse_ipv4(value: str) -> typing.Union[str, None]:
        """
        Parser for IPv4

        Args:
            value (str): The raw value of the IPv4.

        Returns:
            Validated and stripped IPv4 value, None if not valid.
        """
        stripped_value = value.strip("'")
        valid = validators.ipv4(stripped_value) or validators.ipv4_cidr(stripped_value)
        if valid:
            return stripped_value
        return None

    @staticmethod
    def parse_ipv6(value: str) -> typing.Union[str, None]:
        """
        Parser for IPv6

        Args:
            value (str): The raw value of the IPv6.

        Returns:
            Validated and stripped IPv6 value, None if not valid.
        """
        stripped_value = value.strip("'")
        valid = validators.ipv6(stripped_value) or validators.ipv6_cidr(stripped_value)
        if valid:
            return stripped_value
        return None

    @staticmethod
    def parse_url(value: str) -> typing.Union[str, None]:
        """
        Parser for a URL

        Args:
            value (str): The raw value of the URL.

        Returns:
            Validated and stripped URL value, None if not valid.
        """
        stripped_value = value.strip("'")
        valid = validators.url(stripped_value)
        if valid:
            return stripped_value
        return None

    @staticmethod
    def parse_domain(value: str) -> typing.Union[str, None]:
        """
        Parser for a Domain

        Args:
            value (str): The raw value of the Domain.

        Returns:
            Validated and stripped Domain value, None if not valid.
        """
        stripped_value = value.strip("'")
        valid = validators.domain(stripped_value)
        if valid:
            return stripped_value
        return None

    @staticmethod
    def parse_md5(value: str) -> typing.Union[str, None]:
        """
        Parser for MD5 Hash

        Args:
            value (str): The raw value of the MD5 Hash.

        Returns:
            Validated and stripped MD5 Hash value, None if not valid.
        """
        stripped_value = value.strip("'")
        valid = validators.md5(stripped_value)
        if valid:
            return stripped_value
        return None

    @staticmethod
    def parse_sha256(value: str) -> typing.Union[str, None]:
        """
        Parser for SHA256 Hash

        Args:
            value (str): The raw value of the SHA256 Hash.

        Returns:
            Validated and stripped SHA256 Hash value, None if not valid.
        """
        stripped_value = value.strip("'")
        valid = validators.sha256(stripped_value)
        if valid:
            return stripped_value
        return None


class STIXPatternParser(STIXPatternListener):
    """
    STIXPatternListener extender for the custom parsing of the
    STIX Pattern.
    """
    def __init__(self) -> None:
        self.matched_iocs = []

    def enterPropTestEqual(self, context) -> None:
        """
        Entering the properties of a STIX Pattern.

        Args:
            context: The STIX Pattern Context

        Returns:
            None
        """
        parts = [child.getText() for child in context.getChildren()]
        # Getting the parts which are:
        # [0]: The stix field type (eg. `ivp4-addr:value`)
        # [1]: Always `=` sign
        # [2]: The value inside single quotes (eg. `'127.0.0.1'`)
        if parts and len(parts) == 3:
            stix_field_type = parts[0]
            stix_field_value = parts[2]
            ioc_parser_value = IOCPatternParser(
                stix_field_type, stix_field_value
            ).parse()
            if ioc_parser_value:
                self.matched_iocs.append(ioc_parser_value)

    def enterPattern(self, *args, **kwargs):
        """
        Resetting the `matched_iocs` variable whenever we enter a pattern.
        """
        self.matched_iocs = []
