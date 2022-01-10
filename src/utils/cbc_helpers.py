from cbc_sdk.enterprise_edr import Feed


def get_feed(cb, feed_name=None, feed_id=None):
    if feed_id:
        return cb.select(Feed, feed_id)
    elif feed_name:
        feeds = [feed for feed in cb.select(Feed) if feed.name == feed_name]

        if not feeds:
            print("No feeds named '{}'".format(feed_name))
        elif len(feeds) > 1:
            print("More than one feed named '{}'".format(feed_name))
        return feeds[0]
    else:
        raise ValueError("expected either feed_id or feed_name")
