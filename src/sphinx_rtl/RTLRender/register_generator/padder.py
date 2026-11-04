# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    04/11/2026
#
# Brief :   Generate the padded register map, ready to be rendered.
# ----------------------------------------------------------------------------


def compute_register_layout(registers: list[tuple[str, int, int, str]]) -> list[dict]:
    """
    Build the correct representation of registers prior building the headers.
    """

    sorted_regs = sorted(registers, key=lambda x: x[1])

    packed_fields = []
    current_offset = 0
    pad_counter = 0

    for name, offset, size_bits, description in sorted_regs:
        size_bytes = size_bits // 8

        if offset > current_offset:
            pad_size = offset - current_offset
            packed_fields.append(
                {
                    "name": f"_reserved_{pad_counter}",
                    "offset": current_offset,
                    "size_bytes": pad_size,
                    "is_padding": True,
                    "description": f"Reserved / Padding gap of {pad_size} bytes",
                }
            )
            pad_counter += 1
            current_offset = offset

        packed_fields.append(
            {
                "name": name.lower(),
                "offset": offset,
                "size_bytes": size_bytes,
                "is_padding": False,
                "description": description,
            }
        )

        current_offset = offset + size_bytes

    return packed_fields
