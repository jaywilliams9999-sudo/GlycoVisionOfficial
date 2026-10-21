"""Domain errors raised by services. main.py translates them into HTTP status codes."""


class PatientNotFound(Exception):
    pass


class AssessmentNotFound(Exception):
    pass


class UnknownModelVersion(Exception):
    pass


class InvalidInputs(Exception):
    pass