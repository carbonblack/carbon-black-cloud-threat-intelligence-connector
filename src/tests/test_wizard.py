# import pytest

# from src.cli.wizard import main


# class MockFileManager:
#     def __enter__(self):
#         ...

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         ...


# def open_file_mock(*args):
#     return MockFileManager()


# def test_migrate_file_doesnt_exist(monkeypatch):
#     called = False

#     def migrate_input(the_prompt=""):
#         nonlocal called
#         if not called:
#             called = True
#             return "1"
#         return ""

#     monkeypatch.setattr("builtins.input", migrate_input)
#     monkeypatch.setattr("os.path.exists", lambda x: False)
#     main()


# def test_migrate_file_exists(monkeypatch):
#     called = False
#     dump_called = False

#     def migrate_input(the_prompt=""):
#         nonlocal called
#         if not called:
#             called = True
#             return "1"
#         return ""

#     def dump_method(data, config, **kwargs):
#         expected_data = {
#             "config_path": "config.ini",
#             "sites": [
#                 {
#                     "my_site_name_1": {
#                         "feeds": [
#                             {
#                                 "stix_feed1": {
#                                     "version": 1.2,
#                                     "enabled": True,
#                                     "feed_id": "someid",
#                                     "site": "site.com",
#                                     "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                     "collection_management_path": "/api/v1/taxii/collection_management/",
#                                     "poll_path": "/api/v1/taxii/poll/",
#                                     "use_https": "",
#                                     "ssl_verify": False,
#                                     "cert_file": "",
#                                     "key_file": "",
#                                     "default_score": "",
#                                     "collections": ["collection1"],
#                                     "start_date": "",
#                                     "size_of_request_in_minutes": "",
#                                     "ca_cert": "",
#                                     "http_proxy_url": "",
#                                     "https_proxy_url": "",
#                                     "username": "guest",
#                                     "password": "guest",
#                                 }
#                             }
#                         ]
#                     }
#                 }
#             ],
#         }
#         nonlocal dump_called
#         assert data == expected_data
#         assert kwargs["sort_keys"] is False
#         dump_called = True

#     old_config_data = {
#         "sites": {
#             "my_site_name_1": {
#                 "feed_id": "someid",
#                 "site": "site.com",
#                 "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                 "collection_management_path": "/api/v1/taxii/collection_management/",
#                 "poll_path": "/api/v1/taxii/poll/",
#                 "use_https": None,
#                 "ssl_verify": False,
#                 "cert_file": None,
#                 "key_file": None,
#                 "default_score": None,
#                 "username": "guest",
#                 "password": "guest",
#                 "collections": "collection1",
#                 "start_date": None,
#                 "size_of_request_in_minutes": None,
#                 "ca_cert": None,
#                 "http_proxy_url": None,
#                 "https_proxy_url": None,
#             }
#         }
#     }

#     monkeypatch.setattr("builtins.input", migrate_input)
#     monkeypatch.setattr("yaml.safe_load", lambda x: old_config_data)
#     monkeypatch.setattr("yaml.dump", dump_method)
#     monkeypatch.setattr("os.path.exists", lambda x: True)
#     monkeypatch.setattr("builtins.open", open_file_mock)
#     main()
#     assert dump_called


# def test_generate_config(monkeypatch):
#     called = -1
#     dump_called = False

#     def generate_config_input(the_prompt=""):
#         inputs = [
#             "2",
#             "y",
#             "my_site_name_1",
#             "1",
#             "feed1",
#             "",
#             "",
#             "feedid1",
#             "site2.com",
#             "/api/v1/taxii/taxii-discovery-service/",
#             "",
#             "",
#             "",
#             "",
#             "",
#             "",
#             "",
#             "",
#             "",
#             "",
#             "",
#             "",
#             "",
#             "guest1",
#             "guest1",
#             "2",
#             "myfeed3",
#             "",
#             "",
#             "feedid2",
#             "site2.com",
#             "/api/v1/taxii/taxii-discovery-service/",
#             "guest",
#             "guest",
#             "0",
#             "",
#         ]
#         nonlocal called
#         called += 1
#         return inputs[called]

#     def dump_method(data, config, **kwargs):
#         expected_data = {
#             "config_path": "config.ini",
#             "sites": [
#                 {
#                     "my_site_name_1": {
#                         "feeds": [
#                             {
#                                 "feed1": {
#                                     "version": 1.2,
#                                     "enabled": True,
#                                     "feed_id": "feedid1",
#                                     "site": "site2.com",
#                                     "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                     "collection_management_path": "",
#                                     "poll_path": "",
#                                     "use_https": "",
#                                     "ssl_verify": False,
#                                     "cert_file": "",
#                                     "key_file": "",
#                                     "default_score": "",
#                                     "collections": [],
#                                     "start_date": "",
#                                     "size_of_request_in_minutes": "",
#                                     "ca_cert": "",
#                                     "http_proxy_url": "",
#                                     "https_proxy_url": "",
#                                     "username": "guest1",
#                                     "password": "guest1",
#                                 }
#                             },
#                             {
#                                 "myfeed3": {
#                                     "version": 2.0,
#                                     "enabled": True,
#                                     "feed_id": "feedid2",
#                                     "site": "site2.com",
#                                     "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                     "username": "guest",
#                                     "password": "guest",
#                                 }
#                             },
#                         ]
#                     }
#                 }
#             ],
#         }
#         nonlocal dump_called
#         assert data == expected_data
#         assert kwargs["sort_keys"] is False
#         dump_called = True

#     monkeypatch.setattr("builtins.input", generate_config_input)
#     monkeypatch.setattr("os.path.exists", lambda x: False)
#     monkeypatch.setattr("yaml.dump", dump_method)
#     monkeypatch.setattr("builtins.open", open_file_mock)
#     main()
#     assert dump_called


# def test_update_config_add_feed(monkeypatch):
#     load_data = {
#         "config_path": "config.ini",
#         "sites": [
#             {
#                 "my_site_name_1": {
#                     "feeds": [
#                         {
#                             "stix_feed1": {
#                                 "version": 1.2,
#                                 "enabled": True,
#                                 "feed_id": "jf1SF7iTSopX9wLUJ8cqg",
#                                 "site": "limo.anomali.com",
#                                 "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                 "collection_management_path": "/api/v1/taxii/collection_management/",
#                                 "poll_path": "/api/v1/taxii/poll/",
#                                 "use_https": "",
#                                 "ssl_verify": False,
#                                 "cert_file": "",
#                                 "key_file": "",
#                                 "default_score": "",
#                                 "collections": ["ISO_CBC_Export_Filter_S7085"],
#                                 "start_date": "",
#                                 "size_of_request_in_minutes": "",
#                                 "ca_cert": "",
#                                 "http_proxy_url": "",
#                                 "https_proxy_url": "",
#                                 "username": "guest",
#                                 "password": "guest",
#                             }
#                         }
#                     ]
#                 }
#             }
#         ],
#     }

#     called = -1
#     dump_called = False

#     def update_config_input(the_prompt=""):
#         inputs = [
#             "3",
#             "2",
#             "1",
#             "2",
#             "myfeed3",
#             "",
#             "",
#             "feedid2",
#             "site2.com",
#             "/api/v1/taxii/taxii-discovery-service/",
#             "guest1",
#             "guest1",
#             "0",
#         ]
#         nonlocal called
#         called += 1
#         return inputs[called]

#     def dump_method(data, config, **kwargs):
#         expected_data = {
#             "config_path": "config.ini",
#             "sites": [
#                 {
#                     "my_site_name_1": {
#                         "feeds": [
#                             {
#                                 "stix_feed1": {
#                                     "version": 1.2,
#                                     "enabled": True,
#                                     "feed_id": "jf1SF7iTSopX9wLUJ8cqg",
#                                     "site": "limo.anomali.com",
#                                     "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                     "collection_management_path": "/api/v1/taxii/collection_management/",
#                                     "poll_path": "/api/v1/taxii/poll/",
#                                     "use_https": "",
#                                     "ssl_verify": False,
#                                     "cert_file": "",
#                                     "key_file": "",
#                                     "default_score": "",
#                                     "collections": ["ISO_CBC_Export_Filter_S7085"],
#                                     "start_date": "",
#                                     "size_of_request_in_minutes": "",
#                                     "ca_cert": "",
#                                     "http_proxy_url": "",
#                                     "https_proxy_url": "",
#                                     "username": "guest",
#                                     "password": "guest",
#                                 }
#                             },
#                             {
#                                 "myfeed3": {
#                                     "version": 2.0,
#                                     "enabled": True,
#                                     "feed_id": "feedid2",
#                                     "site": "site2.com",
#                                     "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                     "username": "guest1",
#                                     "password": "guest1",
#                                 }
#                             },
#                         ]
#                     }
#                 }
#             ],
#         }
#         nonlocal dump_called
#         assert data == expected_data
#         assert kwargs["sort_keys"] is False
#         dump_called = True

#     monkeypatch.setattr("builtins.input", update_config_input)
#     monkeypatch.setattr("os.path.exists", lambda x: False)
#     monkeypatch.setattr("yaml.dump", dump_method)
#     monkeypatch.setattr("yaml.safe_load", lambda x: load_data)
#     monkeypatch.setattr("builtins.open", open_file_mock)
#     main()
#     assert dump_called


# def test_update_config_add_new_site(monkeypatch):
#     load_data = {
#         "config_path": "config.ini",
#         "sites": [
#             {
#                 "my_site_name_1": {
#                     "feeds": [
#                         {
#                             "stix_feed1": {
#                                 "version": 1.2,
#                                 "enabled": True,
#                                 "feed_id": "jf1SF7iTSopX9wLUJ8cqg",
#                                 "site": "limo.anomali.com",
#                                 "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                 "collection_management_path": "/api/v1/taxii/collection_management/",
#                                 "poll_path": "/api/v1/taxii/poll/",
#                                 "use_https": "",
#                                 "ssl_verify": False,
#                                 "cert_file": "",
#                                 "key_file": "",
#                                 "default_score": "",
#                                 "collections": ["ISO_CBC_Export_Filter_S7085"],
#                                 "start_date": "",
#                                 "size_of_request_in_minutes": "",
#                                 "ca_cert": "",
#                                 "http_proxy_url": "",
#                                 "https_proxy_url": "",
#                                 "username": "guest",
#                                 "password": "guest",
#                             }
#                         }
#                     ]
#                 }
#             }
#         ],
#     }
#     called = -1
#     dump_called = False

#     def update_config_input(the_prompt=""):
#         inputs = [
#             "3",
#             "1",
#             "y",
#             "my_second_site",
#             "2",
#             "myfeed42",
#             "",
#             "",
#             "feedid2",
#             "site2.com",
#             "/api/v1/taxii/taxii-discovery-service/",
#             "guest1",
#             "guest1",
#             "0",
#             "",
#         ]
#         nonlocal called
#         called += 1
#         return inputs[called]

#     def dump_method(data, config, **kwargs):
#         expected_data = {
#             "config_path": "config.ini",
#             "sites": [
#                 {
#                     "my_site_name_1": {
#                         "feeds": [
#                             {
#                                 "stix_feed1": {
#                                     "version": 1.2,
#                                     "enabled": True,
#                                     "feed_id": "jf1SF7iTSopX9wLUJ8cqg",
#                                     "site": "limo.anomali.com",
#                                     "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                     "collection_management_path": "/api/v1/taxii/collection_management/",
#                                     "poll_path": "/api/v1/taxii/poll/",
#                                     "use_https": "",
#                                     "ssl_verify": False,
#                                     "cert_file": "",
#                                     "key_file": "",
#                                     "default_score": "",
#                                     "collections": ["ISO_CBC_Export_Filter_S7085"],
#                                     "start_date": "",
#                                     "size_of_request_in_minutes": "",
#                                     "ca_cert": "",
#                                     "http_proxy_url": "",
#                                     "https_proxy_url": "",
#                                     "username": "guest",
#                                     "password": "guest",
#                                 }
#                             }
#                         ]
#                     },
#                 },
#                 {
#                     "my_second_site": {
#                         "feeds": [
#                             {
#                                 "myfeed42": {
#                                     "version": 2.0,
#                                     "enabled": True,
#                                     "feed_id": "feedid2",
#                                     "site": "site2.com",
#                                     "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                     "username": "guest1",
#                                     "password": "guest1",
#                                 }
#                             },
#                         ]
#                     }
#                 },
#             ],
#         }
#         nonlocal dump_called
#         assert data == expected_data
#         assert kwargs["sort_keys"] is False
#         dump_called = True

#     monkeypatch.setattr("builtins.input", update_config_input)
#     monkeypatch.setattr("os.path.exists", lambda x: False)
#     monkeypatch.setattr("yaml.dump", dump_method)
#     monkeypatch.setattr("yaml.safe_load", lambda x: load_data)
#     monkeypatch.setattr("builtins.open", open_file_mock)
#     main()
#     assert dump_called


# def test_update_config_add_feed_wrong_choice(monkeypatch):
#     load_data = {
#         "config_path": "config.ini",
#         "sites": [
#             {
#                 "my_site_name_1": {
#                     "feeds": [
#                         {
#                             "stix_feed1": {
#                                 "version": 1.2,
#                                 "enabled": True,
#                                 "feed_id": "jf1SF7iTSopX9wLUJ8cqg",
#                                 "site": "limo.anomali.com",
#                                 "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                 "collection_management_path": "/api/v1/taxii/collection_management/",
#                                 "poll_path": "/api/v1/taxii/poll/",
#                                 "use_https": "",
#                                 "ssl_verify": False,
#                                 "cert_file": "",
#                                 "key_file": "",
#                                 "default_score": "",
#                                 "collections": ["ISO_CBC_Export_Filter_S7085"],
#                                 "start_date": "",
#                                 "size_of_request_in_minutes": "",
#                                 "ca_cert": "",
#                                 "http_proxy_url": "",
#                                 "https_proxy_url": "",
#                                 "username": "guest",
#                                 "password": "guest",
#                             }
#                         }
#                     ]
#                 }
#             }
#         ],
#     }

#     called = -1
#     dump_called = False

#     def update_config_input(the_prompt=""):
#         inputs = ["3", "2", "10"]
#         nonlocal called
#         called += 1
#         return inputs[called]

#     def dump_method(data, config, **kwargs):
#         nonlocal dump_called
#         dump_called = True

#     monkeypatch.setattr("builtins.input", update_config_input)
#     monkeypatch.setattr("os.path.exists", lambda x: False)
#     monkeypatch.setattr("yaml.dump", dump_method)
#     monkeypatch.setattr("yaml.safe_load", lambda x: load_data)
#     monkeypatch.setattr("builtins.open", open_file_mock)
#     main()
#     assert dump_called is False


# def test_update_config_add_new_site(monkeypatch):
#     load_data = {
#         "config_path": "config.ini",
#         "sites": [
#             {
#                 "my_site_name_1": {
#                     "feeds": [
#                         {
#                             "stix_feed1": {
#                                 "version": 1.2,
#                                 "enabled": True,
#                                 "feed_id": "jf1SF7iTSopX9wLUJ8cqg",
#                                 "site": "limo.anomali.com",
#                                 "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                 "collection_management_path": "/api/v1/taxii/collection_management/",
#                                 "poll_path": "/api/v1/taxii/poll/",
#                                 "use_https": "",
#                                 "ssl_verify": False,
#                                 "cert_file": "",
#                                 "key_file": "",
#                                 "default_score": "",
#                                 "collections": ["ISO_CBC_Export_Filter_S7085"],
#                                 "start_date": "",
#                                 "size_of_request_in_minutes": "",
#                                 "ca_cert": "",
#                                 "http_proxy_url": "",
#                                 "https_proxy_url": "",
#                                 "username": "guest",
#                                 "password": "guest",
#                             }
#                         }
#                     ]
#                 }
#             }
#         ],
#     }
#     called = -1
#     dump_called = False

#     def update_config_input(the_prompt=""):
#         inputs = [
#             "3",
#             "1",
#             "y",
#             "my_second_site",
#             "2",
#             "myfeed42",
#             "",
#             "",
#             "feedid2",
#             "site2.com",
#             "/api/v1/taxii/taxii-discovery-service/",
#             "guest1",
#             "guest1",
#             "0",
#             "",
#         ]
#         nonlocal called
#         called += 1
#         return inputs[called]

#     def dump_method(data, config, **kwargs):
#         expected_data = {
#             "config_path": "config.ini",
#             "sites": [
#                 {
#                     "my_site_name_1": {
#                         "feeds": [
#                             {
#                                 "stix_feed1": {
#                                     "version": 1.2,
#                                     "enabled": True,
#                                     "feed_id": "jf1SF7iTSopX9wLUJ8cqg",
#                                     "site": "limo.anomali.com",
#                                     "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                     "collection_management_path": "/api/v1/taxii/collection_management/",
#                                     "poll_path": "/api/v1/taxii/poll/",
#                                     "use_https": "",
#                                     "ssl_verify": False,
#                                     "cert_file": "",
#                                     "key_file": "",
#                                     "default_score": "",
#                                     "collections": ["ISO_CBC_Export_Filter_S7085"],
#                                     "start_date": "",
#                                     "size_of_request_in_minutes": "",
#                                     "ca_cert": "",
#                                     "http_proxy_url": "",
#                                     "https_proxy_url": "",
#                                     "username": "guest",
#                                     "password": "guest",
#                                 }
#                             }
#                         ]
#                     },
#                 },
#                 {
#                     "my_second_site": {
#                         "feeds": [
#                             {
#                                 "myfeed42": {
#                                     "version": 2.0,
#                                     "enabled": True,
#                                     "feed_id": "feedid2",
#                                     "site": "site2.com",
#                                     "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                     "username": "guest1",
#                                     "password": "guest1",
#                                 }
#                             },
#                         ]
#                     }
#                 },
#             ],
#         }
#         nonlocal dump_called
#         assert data == expected_data
#         assert kwargs["sort_keys"] is False
#         dump_called = True

#     monkeypatch.setattr("builtins.input", update_config_input)
#     monkeypatch.setattr("os.path.exists", lambda x: False)
#     monkeypatch.setattr("yaml.dump", dump_method)
#     monkeypatch.setattr("yaml.safe_load", lambda x: load_data)
#     monkeypatch.setattr("builtins.open", open_file_mock)
#     main()
#     assert dump_called


# def test_update_config_wrong_choice(monkeypatch):
#     load_data = {
#         "config_path": "config.ini",
#         "sites": [
#             {
#                 "my_site_name_1": {
#                     "feeds": [
#                         {
#                             "stix_feed1": {
#                                 "version": 1.2,
#                                 "enabled": True,
#                                 "feed_id": "jf1SF7iTSopX9wLUJ8cqg",
#                                 "site": "limo.anomali.com",
#                                 "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                 "collection_management_path": "/api/v1/taxii/collection_management/",
#                                 "poll_path": "/api/v1/taxii/poll/",
#                                 "use_https": "",
#                                 "ssl_verify": False,
#                                 "cert_file": "",
#                                 "key_file": "",
#                                 "default_score": "",
#                                 "collections": ["ISO_CBC_Export_Filter_S7085"],
#                                 "start_date": "",
#                                 "size_of_request_in_minutes": "",
#                                 "ca_cert": "",
#                                 "http_proxy_url": "",
#                                 "https_proxy_url": "",
#                                 "username": "guest",
#                                 "password": "guest",
#                             }
#                         }
#                     ]
#                 }
#             }
#         ],
#     }
#     called = -1
#     dump_called = False

#     def update_config_input(the_prompt=""):
#         inputs = ["3", "a"]
#         nonlocal called
#         called += 1
#         return inputs[called]

#     def dump_method(data, config, **kwargs):
#         expected_data = {
#             "config_path": "config.ini",
#             "sites": [
#                 {
#                     "my_site_name_1": {
#                         "feeds": [
#                             {
#                                 "stix_feed1": {
#                                     "version": 1.2,
#                                     "enabled": True,
#                                     "feed_id": "jf1SF7iTSopX9wLUJ8cqg",
#                                     "site": "limo.anomali.com",
#                                     "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                     "collection_management_path": "/api/v1/taxii/collection_management/",
#                                     "poll_path": "/api/v1/taxii/poll/",
#                                     "use_https": "",
#                                     "ssl_verify": False,
#                                     "cert_file": "",
#                                     "key_file": "",
#                                     "default_score": "",
#                                     "collections": ["ISO_CBC_Export_Filter_S7085"],
#                                     "start_date": "",
#                                     "size_of_request_in_minutes": "",
#                                     "ca_cert": "",
#                                     "http_proxy_url": "",
#                                     "https_proxy_url": "",
#                                     "username": "guest",
#                                     "password": "guest",
#                                 }
#                             }
#                         ]
#                     },
#                 },
#                 {
#                     "my_second_site": {
#                         "feeds": [
#                             {
#                                 "myfeed42": {
#                                     "version": 2.0,
#                                     "enabled": True,
#                                     "feed_id": "feedid2",
#                                     "site": "site2.com",
#                                     "discovery_path": "/api/v1/taxii/taxii-discovery-service/",
#                                     "username": "guest1",
#                                     "password": "guest1",
#                                 }
#                             },
#                         ]
#                     }
#                 },
#             ],
#         }
#         nonlocal dump_called
#         assert data == expected_data
#         assert kwargs["sort_keys"] is False
#         dump_called = True

#     monkeypatch.setattr("builtins.input", update_config_input)
#     monkeypatch.setattr("os.path.exists", lambda x: False)
#     monkeypatch.setattr("yaml.dump", dump_method)
#     monkeypatch.setattr("yaml.safe_load", lambda x: load_data)
#     monkeypatch.setattr("builtins.open", open_file_mock)
#     main()
#     assert dump_called is False


# def test_generate_config_no_site(monkeypatch):
#     called = -1
#     dump_called = False

#     def generate_config_input(the_prompt=""):
#         inputs = ["2", "n"]
#         nonlocal called
#         called += 1
#         return inputs[called]

#     def dump_method(data, config, **kwargs):
#         expected_data = {
#             "config_path": "config.ini",
#             "sites": [],
#         }
#         nonlocal dump_called
#         assert data == expected_data
#         assert kwargs["sort_keys"] is False
#         dump_called = True

#     monkeypatch.setattr("builtins.input", generate_config_input)
#     monkeypatch.setattr("os.path.exists", lambda x: False)
#     monkeypatch.setattr("yaml.dump", dump_method)
#     monkeypatch.setattr("builtins.open", open_file_mock)
#     main()
#     assert dump_called


# def test_exit(monkeypatch):
#     called = False

#     def wrong_and_exit_input():
#         nonlocal called
#         if called:
#             return "0"
#         called = True
#         return "a"

#     monkeypatch.setattr("builtins.input", wrong_and_exit_input)

#     with pytest.raises(SystemExit):
#         main()
