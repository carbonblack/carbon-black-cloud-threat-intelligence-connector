MIGRATED_DATA = {
    "cbc_auth_profile": "default",
    "servers": [
        {
            "name": "my_site_name_1",
            "version": 1.2,
            "enabled": True,
            "cbc_feed_options": {
                "feed_base_name": "my_base_name (2.0) 2022-01-27 to 2022-02-27 - Part 1",
                "category": "STIX Feed",
                "summary": "STIX Feed",
                "severity": 5,
                "feed_id": "90TuDxDYQtiGyg5qhwYCg",
            },
            "proxies": {"http": "http://proxy:8080", "https": "http://proxy:8080"},
            "connection": {
                "host": "site.com",
                "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                "port": None,
                "use_https": True,
                "headers": None,
                "timeout": None,
            },
            "auth": {
                "username": "guest",
                "password": "guest",
                "cert_file": None,
                "key_file": None,
                "ca_cert": None,
                "key_password": None,
                "jwt_auth_url": None,
                "verify_ssl": True,
            },
            "options": {
                "begin_date": None,
                "end_date": None,
                "collection_management_uri": None,
                "collections": ["collection1"],
            },
        }
    ],
}

MIGRATED_DATA_NO_PROXY = {
    "cbc_auth_profile": "default",
    "servers": [
        {
            "name": "my_site_name_1",
            "version": 1.2,
            "enabled": True,
            "cbc_feed_options": {
                "feed_base_name": "my_base_name (2.0) 2022-01-27 to 2022-02-27 - Part 1",
                "category": "STIX Feed",
                "summary": "STIX Feed",
                "severity": 5,
                "feed_id": "90TuDxDYQtiGyg5qhwYCg",
            },
            "proxies": {},
            "connection": {
                "host": "site.com",
                "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                "port": None,
                "use_https": True,
                "headers": None,
                "timeout": None,
            },
            "auth": {
                "username": "guest",
                "password": "guest",
                "cert_file": None,
                "key_file": None,
                "ca_cert": None,
                "key_password": None,
                "jwt_auth_url": None,
                "verify_ssl": True,
            },
            "options": {
                "begin_date": None,
                "end_date": None,
                "collection_management_uri": None,
                "collections": ["collection1"],
            },
        }
    ],
}

OLD_CONFIG_DATA = {
    "sites": {
        "my_site_name_1": {
            "feed_id": "90TuDxDYQtiGyg5qhwYCg",
            "site": "site.com",
            "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
            "collection_management_path": "/api/v1/taxii/collection_management/",
            "poll_path": "/api/v1/taxii/poll/",
            "use_https": None,
            "ssl_verify": False,
            "cert_file": None,
            "key_file": None,
            "default_score": None,
            "username": "guest",
            "password": "guest",
            "collections": "collection1",
            "start_date": None,
            "size_of_request_in_minutes": None,
            "ca_cert": None,
            "http_proxy_url": "http://proxy:8080",
            "https_proxy_url": "http://proxy:8080",
        }
    }
}

OLD_CONFIG_DATA_NO_PROXY = {
    "sites": {
        "my_site_name_1": {
            "feed_id": "90TuDxDYQtiGyg5qhwYCg",
            "site": "site.com",
            "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
            "collection_management_path": "/api/v1/taxii/collection_management/",
            "poll_path": "/api/v1/taxii/poll/",
            "use_https": None,
            "ssl_verify": False,
            "cert_file": None,
            "key_file": None,
            "default_score": None,
            "username": "guest",
            "password": "guest",
            "collections": "collection1",
            "start_date": None,
            "size_of_request_in_minutes": None,
            "ca_cert": None,
            "http_proxy_url": "",
            "https_proxy_url": "",
        }
    }
}

CREATE_CONFIG_DATA = {
    "cbc_auth_profile": "default",
    "servers": [
        {
            "name": "my_site_name_1",
            "version": 1.2,
            "enabled": True,
            "cbc_feed_options": {
                "feed_base_name": "basename",
                "category": "STIX Feed",
                "summary": "STIX Feed",
                "severity": 6,
                "feed_id": "someid",
            },
            "proxies": {"http": "http://some:8080", "https": "http://some:8080"},
            "connection": {
                "host": "site2.com",
                "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                "port": 8080,
                "use_https": True,
                "headers": None,
                "timeout": None,
            },
            "auth": {
                "username": "guest",
                "password": "guest",
                "cert_file": None,
                "key_file": None,
                "ca_cert": None,
                "key_password": None,
                "jwt_auth_url": None,
                "verify_ssl": True,
            },
            "options": {
                "begin_date": None,
                "end_date": None,
                "collection_management_uri": None,
                "collections": "*",
            },
        },
        {
            "name": "my_site_name_3",
            "version": 1.2,
            "enabled": True,
            "cbc_feed_options": {
                "feed_base_name": "basename",
                "category": "STIX Feed",
                "summary": "STIX Feed",
                "severity": 6,
                "feed_id": "someid",
            },
            "proxies": {},
            "connection": {
                "host": "site2.com",
                "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                "port": 8080,
                "use_https": True,
                "headers": None,
                "timeout": None,
            },
            "auth": {
                "username": "guest",
                "password": "guest",
                "cert_file": None,
                "key_file": None,
                "ca_cert": None,
                "key_password": None,
                "jwt_auth_url": None,
                "verify_ssl": True,
            },
            "options": {
                "begin_date": None,
                "end_date": None,
                "collection_management_uri": None,
                "collections": "*",
            },
        },
        {
            "name": "my_site_name_2",
            "version": 2.0,
            "enabled": True,
            "cbc_feed_options": {
                "feed_base_name": "basename2",
                "category": "STIX Feed",
                "summary": "STIX Feed",
                "severity": 5,
                "feed_id": "someid",
            },
            "connection": {"url": "site2.com"},
            "proxies": {},
            "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
            "options": {
                "added_after": None,
                "roots": [{"title": "my_api_route", "collections": ["col1", "col2"]}],
            },
        },
    ],
}

UPDATE_CONFIG_DATA_INIT = {
    "cbc_auth_profile": "default",
    "servers": [
        {
            "name": "my_site_name_1",
            "version": 1.2,
            "enabled": True,
            "cbc_feed_options": {
                "feed_base_name": "base_name",
                "category": "STIX Feed",
                "summary": "STIX Feed",
                "severity": 5,
                "feed_id": None,
            },
            "proxies": {},
            "connection": {
                "host": "limo.anomali.com",
                "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                "port": None,
                "use_https": True,
                "headers": None,
                "timeout": None,
            },
            "auth": {
                "username": "guest",
                "password": "guest",
                "cert_file": None,
                "key_file": None,
                "ca_cert": None,
                "key_password": None,
                "jwt_auth_url": None,
                "verify_ssl": True,
            },
            "options": {
                "begin_date": None,
                "end_date": None,
                "collection_management_uri": None,
                "collections": ["ISO_CBC_Export_Filter_S7085"],
            },
        }
    ],
}

UPDATE_CONFIG_DATA = {
    "cbc_auth_profile": "default",
    "servers": [
        {
            "name": "my_site_name_1",
            "version": 1.2,
            "enabled": True,
            "cbc_feed_options": {
                "feed_base_name": "base_name",
                "category": "STIX Feed",
                "summary": "STIX Feed",
                "severity": 5,
                "feed_id": None,
            },
            "proxies": {},
            "connection": {
                "host": "limo.anomali.com",
                "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                "port": None,
                "use_https": True,
                "headers": None,
                "timeout": None,
            },
            "auth": {
                "username": "guest",
                "password": "guest",
                "cert_file": None,
                "key_file": None,
                "ca_cert": None,
                "key_password": None,
                "jwt_auth_url": None,
                "verify_ssl": True,
            },
            "options": {
                "begin_date": None,
                "end_date": None,
                "collection_management_uri": None,
                "collections": ["ISO_CBC_Export_Filter_S7085"],
            },
        },
        {
            "name": "my_site_name_2",
            "version": 2.0,
            "enabled": True,
            "cbc_feed_options": {
                "feed_base_name": "basename2",
                "category": "STIX Feed",
                "summary": "STIX Feed",
                "severity": 5,
                "feed_id": "someid",
            },
            "connection": {"url": "site2.com"},
            "proxies": {},
            "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
            "options": {
                "added_after": None,
                "roots": [{"title": "my_api_route", "collections": "*"}],
            },
        },
    ],
}

UPDATE_CONFIG_DATA_NO_ROUTES = {
    "cbc_auth_profile": "default",
    "servers": [
        {
            "name": "my_site_name_1",
            "version": 1.2,
            "enabled": True,
            "cbc_feed_options": {
                "feed_base_name": "base_name",
                "category": "STIX Feed",
                "summary": "STIX Feed",
                "severity": 5,
                "feed_id": None,
            },
            "proxies": {},
            "connection": {
                "host": "limo.anomali.com",
                "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
                "port": None,
                "use_https": True,
                "headers": None,
                "timeout": None,
            },
            "auth": {
                "username": "guest",
                "password": "guest",
                "cert_file": None,
                "key_file": None,
                "ca_cert": None,
                "key_password": None,
                "jwt_auth_url": None,
                "verify_ssl": True,
            },
            "options": {
                "begin_date": None,
                "end_date": None,
                "collection_management_uri": None,
                "collections": ["ISO_CBC_Export_Filter_S7085"],
            },
        },
        {
            "name": "my_site_name_2",
            "version": 2.0,
            "enabled": True,
            "cbc_feed_options": {
                "feed_base_name": "basename2",
                "category": "STIX Feed",
                "summary": "STIX Feed",
                "severity": 5,
                "feed_id": "someid",
            },
            "connection": {"url": "site2.com"},
            "proxies": {},
            "auth": {"username": "guest", "password": "guest", "verify": True, "cert": None},
            "options": {
                "added_after": None,
                "roots": [],
            },
        },
    ],
}
