"""Utilities to unspecific for other modules."""

from typing import Never


def assert_never(arg: Never) -> Never:  # noqa: ARG001
    """Help the type checker perform exhaustiveness checks."""
    raise AssertionError
