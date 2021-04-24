from suncal.models.icalendar import Vcalendar


def test_vcalendar():
    vcal = Vcalendar(x_wr_calname="Sonne", x_wr_timezone="Europe/Berlin")

    assert vcal.x_wr_timezone == "Europe/Berlin"
    assert vcal.method == "PUBLISH"
    assert vcal.prodid == "PLACEHOLDER"
    assert vcal.x_wr_calname == "Sonne"
    assert vcal.cascale == "GREGORIAN"

    assert Vcalendar.footer() == "END:VCALENDAR"
    assert "METHOD:PUBLISH" in vcal.header()
