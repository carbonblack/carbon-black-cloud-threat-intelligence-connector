# -*- coding: utf-8 -*-

# *******************************************************
# Copyright (c) VMware, Inc. 2020-2021. All Rights Reserved.
# SPDX-License-Identifier: MIT
# *******************************************************
# *
# * DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
# * WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
# * EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
# * WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
# * NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.

"""CBC Helpers"""
from cbc_sdk.enterprise_edr import Feed, Watchlist
from cbc_sdk.errors import ObjectNotFoundError, MoreThanOneResultError

"""Feed Helpers"""
# TODO - create, delete


def get_feed(cb, feed_name=None, feed_id=None):
    if feed_id:
        return cb.select(Feed, feed_id)
    elif feed_name:
        feeds = [feed for feed in cb.select(Feed) if feed.name == feed_name]

        if not feeds:
            raise ObjectNotFoundError("No feeds named '{}'".format(feed_name))
        elif len(feeds) > 1:
            raise MoreThanOneResultError(
                "More than one feed named '{}'".format(feed_name)
            )
        return feeds[0]
    else:
        raise ValueError("expected either feed_id or feed_name")


"""Watchlist Helpers"""


def create_watchlist(cb, feed, name="Subscribed feed", description="STIX/TAXII"):
    """Create watchlist from feed"""
    watchlist = Watchlist.create_from_feed(feed, name, description)
    return watchlist.save()

# TODO - enable alerts / disable alerts
