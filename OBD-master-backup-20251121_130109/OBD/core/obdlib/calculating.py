# Calculus and math helpers
def average(values):
    """
    This function receive a LIST parameter and return the average, casting in FLOAT.
    """
    values = list(map(float, values))
    return sum(values)/len(values)
