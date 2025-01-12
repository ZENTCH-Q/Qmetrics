def interpret_sqn(sqn):
    """
    Interpret the SQN score based on the System Quality Number benchmarks in the image.

    Parameters:
    - sqn (float): The calculated SQN value.

    Returns:
    - str: The interpretation of the SQN value.
    """
    if sqn < 1:
        return "Very hard to trade"
    elif 1 <= sqn < 2:
        return "Average"
    elif 2 <= sqn < 3:
        return "Good"
    elif 3 <= sqn < 5:
        return "Excellent"
    elif 5 <= sqn < 7:
        return "Superb"
    else:  # sqn >= 7
        return "Holy Grail"
