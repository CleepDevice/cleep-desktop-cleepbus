#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    "CommandError",
    "CommandInfo",
    "NoResponse",
    "NoMessageAvailable",
    "InvalidParameter",
    "MissingParameter",
    "InvalidMessage",
    "Unauthorized",
    "BusError",
]


class CommandError(Exception):
    """
    Raise when command failed
    """

    def __init__(self, value):
        super().__init__("command failed")
        self.value = value

    def __str__(self):
        return repr(self.value)


class CommandInfo(Exception):
    """
    Raise when command succeed with message to display to user
    """

    def __init__(self, value):
        super().__init__("command succeed")
        self.value = value

    def __str__(self):
        return repr(self.value)


class NoResponse(Exception):
    """
    Raise when command received no response in time
    """

    def __str__(self):
        return repr("No response")


class NoMessageAvailable(Exception):
    """
    Raise when no message is available
    """

    def __str__(self):
        return repr("No message available")


class InvalidParameter(Exception):
    """
    Raise when parameter is invalid
    """

    def __init__(self, value):
        super().__init__("invalid parameter")
        self.value = value

    def __str__(self):
        return repr(self.value)


class MissingParameter(Exception):
    """
    Raise when parameter is missing
    """

    def __init__(self, value):
        super().__init__("missing parameter")
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidMessage(Exception):
    """
    Raise when message is invalid
    """

    def __str__(self):
        return repr("Invalid message")


class BusNotReady(Exception):
    """
    Raise when message bus is not ready
    """

    def __str__(self):
        return repr(
            "Bus is not ready yet. Please handle system.application.ready event before sending events."
        )


class InvalidModule(Exception):
    """
    Raise when invalid module (aka app) is called
    """

    def __init__(self, module):
        super().__init__("invalid module %s", module)
        self.module = module

    def __str__(self):
        return repr(f"Invalid module {self.module} (not loaded or unknown)")


class Unauthorized(Exception):
    """
    Raise when something is unauthorized
    """

    def __init__(self, value):
        super().__init__("unauthorized")
        self.value = value

    def __str__(self):
        return repr(self.value)


class BusError(Exception):
    """
    Raise on bus error
    """

    def __init__(self, value):
        super().__init__("bus error")
        self.value = value

    def __str__(self):
        return repr(self.value)
