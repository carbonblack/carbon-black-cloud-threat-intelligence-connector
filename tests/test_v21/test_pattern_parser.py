from stix_parsers.v21.stix_pattern_parser import IOCPatternParser


def test_pattern_parse():
    pattern_parser = IOCPatternParser("ipv4-addr:value", "'91.121.240.170'").parse()
    assert pattern_parser == {"field": "netconn_ipv4", "value": "91.121.240.170"}


def test_pattern_parse_returns_None(monkeypatch):
    monkeypatch.setattr(
        "stix_parsers.v21.stix_pattern_parser.IOCPatternParser.is_parsable", False
    )
    pattern_parser = IOCPatternParser("ipv4-addr:value", "'91.121.240.170'")
    assert pattern_parser.parse() is None


def test_pattern_parse_is_parsable_False():
    pattern_parser = IOCPatternParser("TEST", "'91.121.240.170'")
    assert pattern_parser.is_parsable is False


def test_pattern_lookup_parser_returns_None():
    pattern_parser = IOCPatternParser("TEST", "'91.121.240.170'")
    assert pattern_parser._parser is None


def test_pattern_parse_ipv4(monkeypatch):
    monkeypatch.setattr("validators.ipv4", lambda *args: False)
    monkeypatch.setattr("validators.ipv4_cidr", lambda *args: False)
    pattern_parser = IOCPatternParser("ipv4-addr:value", "'91.121.240.170'").parse()
    assert pattern_parser is None


def test_pattern_parse_ipv6(monkeypatch):
    monkeypatch.setattr("validators.ipv6", lambda *args: False)
    monkeypatch.setattr("validators.ipv6_cidr", lambda *args: False)
    pattern_parser = IOCPatternParser(
        "ipv6-addr:value", "'2001:0db8:dead:beef:dead:beef:dead:0001/128'"
    ).parse()
    assert pattern_parser is None


def test_pattern_parse_url(monkeypatch):
    monkeypatch.setattr("validators.url", lambda *args: False)
    pattern_parser = IOCPatternParser("url:value", "'http://test.test/1337/'").parse()
    assert pattern_parser is None


def test_pattern_parse_domain(monkeypatch):
    monkeypatch.setattr("validators.domain", lambda *args: False)
    pattern_parser = IOCPatternParser("domain-name:value", "'test.test'").parse()
    assert pattern_parser is None


def test_pattern_parse_md5(monkeypatch):
    monkeypatch.setattr("validators.md5", lambda *args: False)
    pattern_parser = IOCPatternParser(
        "file:hashes.'MD5'", "'d6d9c42d50794f64088f369597b84721'"
    ).parse()
    assert pattern_parser is None


def test_pattern_parse_sha256(monkeypatch):
    monkeypatch.setattr("validators.sha256", lambda *args: False)
    pattern_parser = IOCPatternParser(
        "file:hashes.'SHA-256'",
        "'ef537f25c895bfa782526529a9b63d97aa631564d5d789c2b765448c8635fb6c'",
    ).parse()
    assert pattern_parser is None
