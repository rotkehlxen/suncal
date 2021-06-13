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
