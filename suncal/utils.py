import datetime as dt
from typing import List

def date_range(date_from: dt.date, date_to: dt.date) -> List[dt.date]:
    """
    Create list of dates from [date_from] to [date_to] including the
    from and to dates.
    """
    return [date_from + dt.timedelta(days=i) for i in range((date_to - date_from).days + 1)]
