# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Infer the polarity of some signals.
# ----------------------------------------------------------------------------

# Imports
from ...models import Component
from dataclasses import dataclass
import itertools
from enum import StrEnum
import re

# Configure logger
from sphinx.util import logging

logger = logging.getLogger(__name__)

# Define the pairs
POLARITY_PAIRS = [
    ("p", "n"),
    ("pos", "neg"),
    ("plus", "minus"),
    ("dp", "dn"),
    ("dp", "dm"),
]

# Define the tricks to access the dict faster
POS_TO_NEG = dict(POLARITY_PAIRS)
NEG_TO_POS = {neg: pos for pos, neg in POLARITY_PAIRS}
ALL_POS = set(POS_TO_NEG.keys())
ALL_NEG = set(NEG_TO_POS.keys())
ALL_TAGS = "|".join(sorted(ALL_POS | ALL_NEG, key=len, reverse=True))
RE_DIFF_SUFFIX = re.compile(rf"^(?P<stem>.+)_(?P<tag>{ALL_TAGS})$", re.IGNORECASE)
RE_DIFF_PREFIX = re.compile(rf"^(?P<tag>{ALL_TAGS})_(?P<stem>.+)$", re.IGNORECASE)
RE_SINGLE_NEG = re.compile(
    r"(?:_(?:n|b|bar|l|ni|no)$)"
    r"|^(?:n|b|not|inv)_"
    r"|^(?:a?resetn|rstn|nrst|nreset|ncs|nwe)$",
    re.IGNORECASE,
)


# Define the polarity enum
class Polarity(StrEnum):
    ACTIVE_LOW = "neg"
    ACTIVE_HIGH = "pos"


# Define a temp diff pair class
@dataclass(slots=True)
class DiffPair:
    stem: str
    pos_port: str
    neg_port: str
    kind: str


# Define a temp single pair class
@dataclass(slots=True)
class SinglePort:
    name: str
    polarity: Polarity


# Function
def infer_polarity(component: Component) -> Component:
    """
    Infer the polarity of the different port and signals based on the process triggers lists.

    Notes : Three options are possible at the end, for a simple reason of documentation clobbering.
    Therefore, only _p signals are flagged as positive, and _n signals are flagged as negatives.
    """

    # fetch the names of the different signals and get our output sets
    names = set(x.name for x in itertools.chain(component.signals, component.ports))
    matched = set()
    pairs = dict()

    # First pass for the suffixes
    for name in names:
        if name in matched:
            continue

        m = RE_DIFF_SUFFIX.match(name)
        if not m:
            continue

        stem, tag = m.group("stem"), m.group("tag").lower()

        # Is the signal flagged as positive ?
        if tag in POS_TO_NEG:
            neg_tag = POS_TO_NEG[tag]
            neg_candidate = (
                f"{stem}_{neg_tag.upper()}"
                if m.group("tag").isupper()
                else f"{stem}_{neg_tag}"
            )

            if neg_candidate in names and neg_candidate not in matched:
                diff = DiffPair(
                    stem=stem, pos_port=name, neg_port=neg_candidate, kind="suffix"
                )
                pairs[name] = diff
                pairs[neg_candidate] = diff

                matched.add(name)
                matched.add(neg_candidate)

    # Now, perform a second pass to fetch the prefixes
    for name in sorted(names):
        if name in matched:
            continue

        m = RE_DIFF_PREFIX.match(name)
        if not m:
            continue

        stem, tag = m.group("stem"), m.group("tag").lower()

        if tag in POS_TO_NEG:
            neg_tag = POS_TO_NEG[tag]
            neg_candidate = (
                f"{stem}_{neg_tag.upper()}"
                if m.group("tag").isupper()
                else f"{stem}_{neg_tag}"
            )

            if neg_candidate in names and neg_candidate not in matched:
                diff = DiffPair(
                    stem=stem,
                    pos_port=name,
                    neg_port=neg_candidate,
                    kind="prefix",
                )

                pairs[name] = diff
                pairs[neg_candidate] = diff

                matched.add(name)
                matched.add(neg_candidate)

    # Final unwrap
    singles = dict()
    for name in sorted(names):
        if name not in matched:
            pol = (
                Polarity.ACTIVE_LOW
                if RE_SINGLE_NEG.search(name)
                else Polarity.ACTIVE_HIGH
            )
            singles[name] = SinglePort(name=name, polarity=pol)

    # Finally, unwrap the custom data into our cases :
    count = 0
    for port in component.ports:
        if port.name in singles.keys():
            port.pair = ""
            port.hdl_polarity = (
                "positive"
                if singles[port.name].polarity == Polarity.ACTIVE_HIGH
                else "negative"
            )
            count += 1

        elif port.name in pairs.keys():
            port.pair = pairs[port.name].stem

            # Update the current port
            if port.name == pairs[port.name].pos_port:
                port.hdl_polarity = "positive"
            else:
                port.hdl_polarity = "negative"

            count += 1

    # Final logs
    if count > 0:
        logger.info(f"[INFO] Attached {count} polarities / pairs markers to ports.")

    return component
