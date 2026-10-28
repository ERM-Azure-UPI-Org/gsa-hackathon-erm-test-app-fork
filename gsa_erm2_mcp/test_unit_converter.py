"""Tests for gsa_erm2_unit_converter."""

import pytest

from server import gsa_erm2_unit_converter as convert


@pytest.mark.parametrize(
    "value, from_unit, to_unit, expected",
    [
        # Existing families (regression)
        (100, "celsius", "fahrenheit", 212),
        (0, "celsius", "kelvin", 273.15),
        (1, "km", "m", 1000),
        (1, "miles", "km", 1.609344),
        (1, "kg", "lb", 2.204623),
        # Volume
        (1, "gal", "l", 3.785412),
        (1000, "ml", "l", 1),
        (1, "gal", "fl_oz", 128),
        # Speed
        (36, "km/h", "m/s", 10),
        (60, "mph", "km/h", 96.56064),
        (1, "knots", "km/h", 1.852),
        # Time
        (1, "h", "min", 60),
        (1, "d", "h", 24),
        (90, "s", "min", 1.5),
    ],
)
def test_conversions(value, from_unit, to_unit, expected):
    result = convert(value, from_unit, to_unit)
    assert result["output"] == pytest.approx(expected, rel=1e-6)
    assert result["from_unit"] == from_unit
    assert result["to_unit"] == to_unit


def test_units_are_case_insensitive_and_trimmed():
    assert convert(1, " KM/H ", "M/S")["output"] == pytest.approx(0.277778, rel=1e-5)


def test_cross_family_raises():
    with pytest.raises(ValueError, match="different families"):
        convert(1, "l", "m/s")


def test_unknown_unit_raises():
    with pytest.raises(ValueError, match="Unknown unit"):
        convert(1, "parsec", "s")
