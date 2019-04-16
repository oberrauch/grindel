def f2c(tf):
    """ Converts tempererature from degrees Fahrenheit into degrees Celsius.

    :param tf: (float) tempertaure in degrees Fahrenheit
    :return: (float) tempertaure in degrees Celsius
    """
    tc = (tf - 32) * 5 / 9
    return tc


def c2f(tc):
    """ Converts tempererature from degrees Celsius into degrees Fahrenheit.

    :param tc: (float) temperature in degrees Celsius
    :return: (float) temperature in degrees Fahrenheit
    """
    tf = (tc * 9 / 5) + 32
    return tf


def f2c_assert(tf):
    """ Learning about the 'assert' functionality using the °F to °C converter. """
    # convert temperature
    tc = f2c(tf)
    # check that we provide physical reasonable results (above absolute zero)
    assert tc > -273.15
    return tc


def f2c_raise(tf):
    """ Learning about raising errors using the °F to °C converter. """
    # check for physical reasonable input (above absolute zero)
    if tf < -459.67:
        raise ValueError('Input temperature below absolute zero.')
    # convert temperature
    tc = f2c(tf)
    return tc

