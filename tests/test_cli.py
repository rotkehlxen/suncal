from click.testing import CliRunner

from suncal.suncal import suncal


def test_timezone_parsing():
    # timezone parsing is case-insensitive: "Europe/berlin" will be parsed to the correct IANA timezone string
    # Europe/Berlin
    runner = CliRunner()
    result = runner.invoke(suncal, ["--dev", "--timezone", "Europe/berlin"])
    assert 'Europe/Berlin' in result.output
    assert result.exit_code == 0

    # spelling errors like "-" instead of "/" are NOT corrected
    result = runner.invoke(suncal, ["--dev", "--timezone", "Europe-Berlin"])
    assert result.exit_code == 2
