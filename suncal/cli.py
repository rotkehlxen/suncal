import datetime as dt

import click
import pytz
from click.core import Context as ClickContext
from click.core import Parameter as ClickParameter

from suncal.models.astro import Event


class IANATimeZoneString(click.ParamType):
    name = "IANATimeZoneString"

    def convert(
        self,
        value: str,
        param: ClickParameter | None,
        ctx: ClickContext | None,
    ):

        iana_timezones = pytz.all_timezones
        iana_timezones_lower = [timezone.lower() for timezone in iana_timezones]

        try:
            idx = iana_timezones_lower.index(value.lower())
            return iana_timezones[idx]

        except ValueError:
            self.fail(
                f"{value!r} is not a valid IANA time zone string!", param, ctx
            )


class ClickDate(click.ParamType):
    name = "Date"

    def convert(
        self,
        value: str,
        param: ClickParameter | None,
        ctx: ClickContext | None,
    ):

        try:
            return dt.datetime.strptime(value, '%Y-%m-%d').date()

        except ValueError:
            self.fail(
                f"{value!r} could not be parsed to a date. Required input format is '%Y-%m-%d'!",
                param,
                ctx,
            )


def common_suncal_options(function):
    """Create decorator for click sub-commands that holds all options that are common to the
    api and ics subcommands."""

    function = click.option(
        "--from",
        "from_date",
        type=ClickDate(),
        help="First date for which to create events.",
        required=True,
    )(function)

    function = click.option(
        "--to",
        "to_date",
        type=ClickDate(),
        help="Last date for which to create events.",
        required=True,
    )(function)

    function = click.option(
        "--event",
        "event_name",
        type=click.Choice([e.value for e in list(Event)], case_sensitive=False),
        required=True,
        help="Sun/Moon parameter for which to create calendar events.",
    )(function)

    function = click.option(
        "--long",
        "longitude",
        type=click.FloatRange(min=-180.0, max=180.0),
        help="Longitude as float.",
        required=True,
    )(function)

    function = click.option(
        "--lat",
        "latitude",
        type=click.FloatRange(min=-90.0, max=90.0),
        help="Latitude as float.",
        required=True,
    )(function)

    function = click.option(
        "--timezone",
        "timezone",
        type=IANATimeZoneString(),
        help="IANA timezone string. Only provide this argument if you want to override the timezone which is set "
        "according to your GPS coordinates automatically. Case-insensitive matching enabled.",
        required=False,
    )(function)

    function = click.option('--dev/--no-dev', 'dev_mode', default=False)(
        function
    )

    return function
