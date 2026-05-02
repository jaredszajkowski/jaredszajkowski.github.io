import math


def round_to_nice_value(value):
    """Round a value to a 'nice' number for tick spacing (1, 2, 5 x 10^n)."""
    if value <= 0:
        return value

    # Find order of magnitude
    exp = math.floor(math.log10(value))
    magnitude = 10**exp

    # Get mantissa (value normalized to [1, 10))
    mantissa = value / magnitude

    # Round mantissa to 1, 2, or 5
    if mantissa <= 1:
        nice_mantissa = 0.5
    elif mantissa <= 1.5:
        nice_mantissa = 1
    elif mantissa <= 3:
        nice_mantissa = 2
    elif mantissa <= 10:
        nice_mantissa = 5
    elif mantissa <= 15:
        nice_mantissa = 10
    elif mantissa <= 30:
        nice_mantissa = 20
    else:
        nice_mantissa = 50

    return nice_mantissa * magnitude

if __name__ == "__main__":
    test_values = [0.03, 0.1, 0.15, 0.5, 1, 2.5, 4, 7, 10.0, 12, 25, 60, 150, 400, 700]
    for val in test_values:
        nice_val = round_to_nice_value(val)
        print(f"Original: {val}, Rounded to nice value: {nice_val}")
