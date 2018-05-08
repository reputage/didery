class DideringError(Exception):
    """
    Base Class for didery exceptions

    To use   raise DideringError("Error: message")
    """


class ValidationError(DideringError):
    """
    Validation related errors
    Usage:
        raise ValidationError("error message")
    """
