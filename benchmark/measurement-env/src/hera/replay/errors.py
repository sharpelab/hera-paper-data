"""The one exception the replay tools raise: the cut cannot be made, and why."""


class CutError(Exception):
    """A fact the derivation cannot place. The message names the thing."""
