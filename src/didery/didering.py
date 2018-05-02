class DideringError(Exception):
    """
    Base Class for bluepea exceptions

    To use   raise BluepeaError("Error: message")
    """


class ValidationError(DideringError):
    """
    Validation related errors
    Usage:
        raise ValidationError("error message")
    """
