from cbc_importer.stix_parsers.v2.pattern_parser import STIX2PatternParser


def test_pattern_parse():
    """Test pattern parse."""
    pattern_parser = STIX2PatternParser("ipv4-addr:value", "'91.121.240.170'").parse()
    assert pattern_parser == {"field": "netconn_ipv4", "value": "91.121.240.170"}


def test_pattern_parse_returns_none(monkeypatch):
    """Test parse returning None."""
    monkeypatch.setattr("cbc_importer.stix_parsers.v2.pattern_parser.STIX2PatternParser.is_parsable", False)
    pattern_parser = STIX2PatternParser("ipv4-addr:value", "'91.121.240.170'")
    assert pattern_parser.parse() is None


def test_pattern_parse_is_parsable_false():
    """Test pattern not parsable."""
    pattern_parser = STIX2PatternParser("TEST", "'91.121.240.170'")
    assert pattern_parser.is_parsable is False


def test_pattern_lookup_parser_returns_none():
    """Test lookup parser returning None."""
    pattern_parser = STIX2PatternParser("TEST", "'91.121.240.170'")
    assert pattern_parser._parser is None


def test_pattern_parse_ipv4(monkeypatch):
    """Test parse IPV4."""
    monkeypatch.setattr("validators.ipv4", lambda *args: False)
    monkeypatch.setattr("validators.ipv4_cidr", lambda *args: False)
    pattern_parser = STIX2PatternParser("ipv4-addr:value", "'91.121.240.170'").parse()
    assert pattern_parser is None


def test_pattern_parse_ipv6(monkeypatch):
    """Test parse IPV6."""
    monkeypatch.setattr("validators.ipv6", lambda *args: False)
    monkeypatch.setattr("validators.ipv6_cidr", lambda *args: False)
    pattern_parser = STIX2PatternParser("ipv6-addr:value", "'2001:0db8:dead:beef:dead:beef:dead:0001/128'").parse()
    assert pattern_parser is None


def test_pattern_parse_url(monkeypatch):
    """Test parse URL."""
    monkeypatch.setattr("validators.url", lambda *args: False)
    pattern_parser = STIX2PatternParser("url:value", "'http://test.test/1337/'").parse()
    assert pattern_parser is None


def test_pattern_parse_domain(monkeypatch):
    """Test parse domain."""
    monkeypatch.setattr("validators.domain", lambda *args: False)
    pattern_parser = STIX2PatternParser("domain-name:value", "'test.test'").parse()
    assert pattern_parser is None


def test_pattern_parse_md5(monkeypatch):
    """Test parse md5."""
    monkeypatch.setattr("validators.md5", lambda *args: False)
    pattern_parser = STIX2PatternParser("file:hashes.'MD5'", "'d6d9c42d50794f64088f369597b84721'").parse()
    assert pattern_parser is None


def test_pattern_parse_sha256(monkeypatch):
    """Test parse sha256."""
    monkeypatch.setattr("validators.sha256", lambda *args: False)
    pattern_parser = STIX2PatternParser(
        "file:hashes.'SHA-256'",
        "'ef537f25c895bfa782526529a9b63d97aa631564d5d789c2b765448c8635fb6c'",
    ).parse()
    assert pattern_parser is None
