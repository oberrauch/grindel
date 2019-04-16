from metutils import f2c, c2f
from numpy.testing import assert_allclose

def test_f2c():
    """ Tests the conversion from degrees Fahrenheit to degrees Celsius. """
    assert f2c(32) == 0
    assert_allclose(f2c(-459.67), -273.15, rtol=1e-5)


def test_c2f():
    """ Tests the conversion from degrees Celsius to degrees Fahrenheit. """
    assert c2f(0) == 32
    assert_allclose(c2f(-273.15), -459.67, rtol=1e-5)


def test_f2c_rountrip():
    """ Tests the if conversion from degrees Fahrenheit to degrees Celsius and back is consistent. """
    assert c2f(f2c(32)) == 32
