# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    20/10/2026
#
# Brief :   Define the get_size_type function for VHDL
# ----------------------------------------------------------------------------

# Imports
import re


def standard_split(inp: str) -> tuple[str, list[str]]:
    """
    Does the standard split there !
    """
    raw = inp.removesuffix(";").removesuffix(")").split("(", 1)

    # Is there any to or downto on the string ?
    size_only = (any("to" in x.lower() for x in raw)) or (
        any("downto" in x.lower() for x in raw)
    )

    # Route the request depending on some parameter
    # The condition is applied if there's a single element to use.
    if len(raw) == 2:
        typ = raw[0]
        size = raw[1]
    elif (len(raw) == 1) and size_only:
        typ = ""
        size = raw[0]
    else:
        typ = raw[0]
        size = ""

    # Split the elements and reverse the order if needed
    if "downto" in size:
        size = [x.strip() for x in size.split("downto")]
    elif "DOWNTO" in size:
        size = [x.strip() for x in size.split("DOWNTO")]

    elif "to" in size:
        size = [x.strip() for x in size.split("to")][::-1]
    elif "TO" in size:
        size = [x.strip() for x in size.split("TO")][::-1]
    else:
        size = [size.strip()]

    # Return the elements as requested.
    if size:
        return typ.strip(), size
    else:
        return typ.strip(), []


def get_size_type(inp: str) -> tuple[str, list[str]]:
    """
    Return the a tuple containing the type and then the size of the elements within it.
    """

    # Is there an OF in the string ?
    if "of" in inp.lower():

        # Init memory
        size = []
        current_str = inp.strip()

        # Process OF one by one
        while re.search(r"\bof\b", current_str, re.IGNORECASE):
            dims, current_str = re.split(
                r"\bof\b", current_str, maxsplit=1, flags=re.IGNORECASE
            )

            # For each, process the N-D arrays
            clean_dims = re.sub(r".*\((.*?)\)", r"\1", dims)
            for dim in clean_dims.split(","):
                _, tmp = standard_split(dim)
                size.extend(tmp)

        # Extract the size
        typ, tmp = standard_split(current_str)
        size.extend(tmp)

        # Return the elements
        return typ, size

    else:
        return standard_split(inp)
