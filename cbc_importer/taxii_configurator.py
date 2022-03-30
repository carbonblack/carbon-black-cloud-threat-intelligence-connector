from typing import Union

import arrow
from cabby import Client10, Client11
from taxii2client.v20 import Server as Client20
from taxii2client.v21 import Server as Client21


class TAXIIConfigurator:
    """The TAXIIConfigurator is setting the values that are coming
    from the configuration. It sets the default ones and converts
    the data into the correct objects/formats.
    """

    def __init__(self, configuration: dict) -> None:
        """The constructor for TAXIIConfigurator

        Args:
            configuration (dict): the dictionary of the server's configuration
        """
        self._configuration = configuration
        self.version = self._configuration["version"]
        self.server_name = self._configuration["name"]
        self.enabled = self._configuration["enabled"]
        self.cbc_feed_options = {}
        self.search_options = {}
        self.client = self._get_client()
        self.dates = None
        self._taxii2_init = {}
        self._set_init_values()
        self._authenticate_client()
        self._set_search_options()
        self._set_cbc_feed_options()

    def _get_client(self) -> Union[Client10, Client11, Client20, Client21]:
        """Getting the correct TAXII Client

        Raises:
            ValueError: If the TAXII version is unsupported

        Returns:
            Union[Client10, Client11, Client20, Client21]: The TAXII Client
        """
        if self.version == 1.2 or self.version == 1.1:
            return Client11
        elif self.version == 1.0:
            return Client10
        elif self.version == 2.0:
            return Client20
        elif self.version == 2.1:
            return Client21
        else:
            raise ValueError(f"TAXII Version {self.version} is unsupported!")

    def _set_search_options(self):
        """Setting the search options for the TAXII Server"""
        if self.version < 2.0:
            self._set_default_time_range_taxii1()
            self.search_options["collection_management_uri"] = self._configuration["options"].get(
                "collection_management_uri", None
            )
            self.search_options["begin_date"] = self.dates[0].datetime
            self.search_options["end_date"] = self.dates[1].datetime
            self.search_options["collections"] = self._configuration["options"]["collections"]
        else:
            self._set_default_time_range_taxii2()
            self.search_options["added_after"] = self.dates.datetime
            self.search_options["gather_data"] = self._configuration["options"]["roots"]

    def _set_cbc_feed_options(self) -> None:
        """Setting the CBC Feed Options"""
        self.cbc_feed_options = self._configuration["cbc_feed_options"]

    def _set_default_time_range_taxii1(self) -> None:
        """Setting the default time range for TAXII 1 Server"""
        begin_date = self._configuration["options"].get("begin_date", None)
        end_date = self._configuration["options"].get("end_date", None)
        if begin_date and end_date:
            begin_date = arrow.get(begin_date, tzinfo="UTC")
            end_date = arrow.get(end_date, tzinfo="UTC")
        else:
            # Set the default range to be (now-1month to now)
            begin_date = arrow.utcnow().shift(months=-1)
            end_date = arrow.utcnow()
        self.dates = begin_date, end_date

    def _set_default_time_range_taxii2(self) -> None:
        """Setting the default `added_after` date for TAXII 2 Server"""
        added_after = self._configuration["options"].get("added_after", None)
        if added_after:
            added_after = arrow.get(added_after, tzinfo="UTC")
        else:
            # Set the default to be a month ago
            added_after = arrow.utcnow().shift(months=-1)
        self.dates = added_after

    def _set_init_values(self):
        """Setting the initial values for the Clients"""
        if self.version < 2.0:
            self.client = self.client(**self._configuration["connection"])
            if self._configuration["proxies"]:
                self.client.set_proxies(proxies=self._configuration["proxies"])
        else:
            self._taxii2_init.update({"proxies": self._configuration["proxies"]})

    def _authenticate_client(self):
        """Authenticating the client"""
        if self.version < 2.0:
            self.client.set_auth(**self._configuration["auth"])
        else:
            self._taxii2_init.update(
                {
                    "user": self._configuration["auth"]["username"],
                    "password": self._configuration["auth"]["password"],
                    "verify": self._configuration["auth"]["verify"],
                    "cert": self._configuration["auth"]["cert"],
                }
            )
            self.client = self.client(
                **self._configuration["connection"],
                **self._taxii2_init,
            )
