# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    26/09/2026
#
# Brief :   Fetch the size of a port.
# ----------------------------------------------------------------------------


def get_size(raw: str) -> list[str]:
    """
    Return the list of strings that define the size of an element, according to the spec.

    Examples :
        [      (core_config_pkg::XLEN - 1) : 0] --> ["(core_config_pkg::XLEN - 1)", "0"]
        [    (IF_LEN - 1) : 0][1:0]             --> ["(IF_LEN - 1)", "0", "1", "0"]
        [2]                                     --> ["1", "0"]
        [IF_LEN]                                --> ["(IF_LEN - 1)", "0"]
        [    (IF_LEN - 1) : 1][1:0]             --> ["(IF_LEN - 1)", "1", "1", "0"]
        ""                                      --> ["0", "0"]
    """
    ret_size: list[str] = []

    # Extract each pairs
    size_pairs = [x.strip() for x in raw.replace("[", "").split("]") if len(x) > 0]

    # For each pairs, append one to the port
    if len(size_pairs) > 0:
        for size_pair in size_pairs:
            temp = size_pair.replace("::", ";;")
            bounds = [x.strip() for x in temp.split(":")]

            # If there's at least two bounds
            if len(bounds) >= 2:
                ret_size.append(bounds[0].replace(";;", "::"))
                ret_size.append(bounds[1].replace(";;", "::"))

            # Else treat it as a single bounded element.
            elif len(bounds) == 1:
                try:
                    val = int(bounds[0].replace(";;", "::"))
                    ret_size.append(f"{val - 1}")
                except:
                    ret_size.append(f"({bounds[0].replace(";;", "::")} - 1)")
                ret_size.append("0")

    # The port does not have any dimension. Return a single bit.
    else:
        ret_size = ["0", "0"]

    return ret_size


if __name__ == "__main__":
    print(get_size("         [      (core_config_pkg::XLEN - 1) : 0]"))
    print(get_size("    [    (IF_LEN - 1) : 0][1:0]"))
    print(get_size("    [2]"))
    print(get_size("    [IF_LEN]"))
    print(get_size("    [    (IF_LEN - 1) : 1][1:0]"))
    print(get_size(""))
