from datetime import datetime

READABLE_DT_FORMAT = "%B %d, %Y %H:%M:%S"


def to_str(dt: datetime):
    return dt.strftime(READABLE_DT_FORMAT)
