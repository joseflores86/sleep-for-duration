# sleep_for_duration

Parses a duration string like `5s` or `2m` and suspends execution for that long.

```python
from sleep_for_duration import parse_duration, sleep_for

# Parse only, no sleeping:
seconds = parse_duration("1.5h")   # -> 5400.0

# Sleep for the parsed duration:
sleep_for("2m")                    # blocks for 120 seconds

# Inject a fake sleeper (useful in tests):
received = []
sleep_for("100ms", sleeper=received.append)  # received == [0.1]
```

## Why this exists

A common need in scripts and test harnesses is a one-liner that sleeps for a
human-readable duration. `time.sleep` only takes raw seconds, so every caller
ends up reinventing the same `"5m" -> 300` conversion. This library is that
conversion plus a thin call to `time.sleep`, nothing more.

The trade-off: a single unit per call. `"1m30s"` is rejected rather than
summed. Composing durations is left to the caller (`sleep_for("1m");
sleep_for("30s")`), which keeps the parser small and its errors obvious.

## Edge cases you will hit

- An empty string or whitespace-only string raises `InvalidDurationError`.
- A string with no unit (e.g. `"10"`) is interpreted as seconds. This is
  deliberate; if it surprises you, always pass a unit.
- Negative values are rejected. `time.sleep` would accept them as a no-op on
  most platforms, but this library treats a negative duration as a caller bug.
- The unit is case-insensitive (`2M` == `2m`).
- `sleep_for` accepts a `sleeper` keyword argument so tests can avoid real
  delays. The return value is the number of seconds the sleeper was called with.

## Exports

- `parse_duration(text: str) -> float` — parse a duration string to seconds.
- `sleep_for(text: str, *, sleeper=None) -> float` — parse and sleep, returning
  the seconds slept.
- `InvalidDurationError` — subclass of `ValueError`, raised on bad input.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

