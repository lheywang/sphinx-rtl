# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    20/10/2026
#
# Brief :   Define the get_size_type function for VHDL
# ----------------------------------------------------------------------------


def get_size_type(inp: str) -> tuple[str, list[str]]:
    """
    Return the a tuple containing the type and then the size of the elements within it.
    """

    raw = inp.split("(", 1)

    if len(raw) < 2:
        typ = raw[0]
        size = ""
    else:
        typ, size = raw[:2]

    if "downto" in size:
        size = [x.strip() for x in size.split("downto")]
    elif "DOWNTO" in size:
        size = [x.strip() for x in size.split("DOWNTO")]

    elif "to" in size:
        size = [x.strip() for x in size.split("to")].reverse()
    elif "TO" in size:
        size = [x.strip() for x in size.split("TO")].reverse()
    else:
        size = [size]

    if size:
        return typ, size
    else:
        return typ, []
