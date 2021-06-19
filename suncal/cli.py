import click
import pytz


class IANATimeZoneString(click.ParamType):
    name = "IANATimeZoneString"

    def convert(self, value, param, ctx):

        iana_timezones = pytz.all_timezones
        iana_timezones_lower = [timezone.lower() for timezone in iana_timezones]

        try:
            idx = iana_timezones_lower.index(value.lower())
            return iana_timezones[idx]

        except ValueError:
            self.fail(
                f"{value!r} is not a valid IANA time zone string!", param, ctx
            )


def common_suncal_options(function):
    """Create decorator for click sub-commands that holds all options that are common to the
    api and ics subcommands."""

    function = click.option(
        "--from",
        "from_date",
        type=click.DateTime(),
        help="First date for which to create events.",
    )(function)

    function = click.option(
        "--to",
        "to_date",
        type=click.DateTime(),
        help="Last date for which to create events.",
    )(function)

    function = click.option(
        "--event",
        "event_name",
        type=click.Choice(
            ['sunrise', 'sunset', 'golden-hour-morning', 'golden-hour-evening'],
            case_sensitive=False,
        ),
        required=True,
        help="Calculate start and end time of the selected event.",
    )(function)

    function = click.option(
        "--long",
        "longitude",
        type=click.FloatRange(min=-180.0, max=180.0),
        help="Longitude as float.",
    )(function)

    function = click.option(
        "--lat",
        "latitude",
        type=click.FloatRange(min=-90.0, max=90.0),
        help="Latitude as float.",
    )(function)

    function = click.option('--dev/--no-dev', 'dev_mode', default=False)(
        function
    )

    return function
