def value_of(choices, label):
    """Return the value of the choice from its label"""
    if label is None:
        return None

    for value, key in choices.choices:
        if key == label:
            return value

    raise ValueError(f"Invalid choice {label}")
