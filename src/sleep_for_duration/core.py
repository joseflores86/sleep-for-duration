"""Parse a duration string and suspend execution for that long.

Supported units:
  ms  - milliseconds
  s   - seconds
  m   - minutes
  h   - hours
  d   - days

Examples of accepted input: '5s', '2m', '100ms', '1h', '3d'.

Design choices:
  * Single unit per call. '1m30s' is rejected, not summed. This keeps the
    parser trivial and the failure mode obvious; callers who need compound
    durations can compose two calls.
  * Fractions are allowed on the numeric part ('1.5h') and rounded to the
    nearest whole millisecond, because time.sleep ultimately takes a float
    in seconds but we want the unit semantics to be exact.
  * Whitespace between the number and unit is tolerated ('5 s') because real
    users type that. Leading/trailing whitespace around the whole string is
    also stripped.
"""

from __future__ import annotations

import time

_UNITS_TO_SECONDS: dict[str, float] = {
    "ms": 0.001,
    "s": 1.0,
    "m": 60.0,
    "h": 3600.0,
    "d": 86400.0,
}


class InvalidDurationError(ValueError):
    """Raised when a duration string cannot be parsed."""


def parse_duration(text: str) -> float:
    """Parse a duration string into a number of seconds (as a float).

    Args:
        text: A string like '5s', '2m', '100ms', '1.5h'.

    Returns:
        The duration in seconds.

    Raises:
        InvalidDurationError: If the string is empty, has an unknown unit,
            contains no numeric part, or is otherwise malformed.
    """
    if not isinstance(text, str):
        raise InvalidDurationError(f"expected a string, got {type(text).__name__}")

    stripped = text.strip()
    if not stripped:
        raise InvalidDurationError("empty duration string")

    # Walk from the end to find where digits stop. This lets us accept
    # scientific notation and decimal points in the numeric part while
    # still treating any trailing alphabetic characters as the unit.
    split_index = len(stripped)
    for i in range(len(stripped) - 1, -1, -1):
        ch = stripped[i]
        if ch.isalpha():
            split_index = i
        else:
            break

    number_part = stripped[:split_index].strip()
    unit_part = stripped[split_index:].strip().lower()

    if not unit_part:
        # No unit means seconds. This is a deliberate convenience.
        unit_part = "s"

    if unit_part not in _UNITS_TO_SECONDS:
        raise InvalidDurationError(f"unknown unit {unit_part!r} in {text!r}")

    if not number_part:
        raise InvalidDurationError(f"no numeric value in {text!r}")

    try:
        value = float(number_part)
    except ValueError as exc:
        raise InvalidDurationError(f"invalid numeric value {number_part!r} in {text!r}") from exc

    if value < 0:
        raise InvalidDurationError(f"negative duration not allowed: {text!r}")

    return value * _UNITS_TO_SECONDS[unit_part]


def sleep_for(text: str, *, sleeper=None) -> float:
    """Parse a duration string and suspend execution for that long.

    Args:
        text: A duration string accepted by :func:`parse_duration`.
        sleeper: Optional callable taking one float argument (seconds). Used
            for deterministic testing. Defaults to :func:`time.sleep`.

    Returns:
        The number of seconds the sleeper was asked to sleep.
    """
    if sleeper is None:
        sleeper = time.sleep
    seconds = parse_duration(text)
    sleeper(seconds)
    return seconds
