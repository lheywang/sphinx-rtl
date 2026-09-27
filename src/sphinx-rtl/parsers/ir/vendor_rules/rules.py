# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Define the standard rules for matching the vendors.
#           Cleaner than putting this into the main file ...
# ----------------------------------------------------------------------------

# Imports
from dataclasses import dataclass
from enum import StrEnum
import re


class Vendor(StrEnum):
    """
    Define the known vendors
    """

    XILINX = "XILINX"
    ALTERA = "ALTERA"
    LATTICE = "LATTICE"
    MICROCHIP = "MICROCHIP"
    CADENCE = "CADENCE"
    SYNOPSYS = "SYNOPSYS"


@dataclass(frozen=True)
class VendorRule:
    """
    Define the rules for a vendor.
    """

    vendor: Vendor
    prefixes: tuple[str, ...]
    primitive_pattern: re.Pattern[str] | None = None


RULES: tuple[VendorRule, ...] = (
    # --------------------------------------------
    # AMD / XILINX
    # --------------------------------------------
    VendorRule(
        vendor=Vendor.XILINX,
        prefixes=(
            "xpm_",
            "blk_mem_gen",
            "dist_mem_gen",
            "fifo_generator",
            "axis_data_fifo",
            "clk_wiz",
        ),
        primitive_pattern=re.compile(
            r"^("
            r"BUFG(_[A-Z0-9]+)?|"
            r"LUT[1-6](_[A-Z0-9]+)?|"
            r"FD[RSCPE]{2,4}|"
            r"DSP48(E[1-4])?|"
            r"RAMB(18|36)[A-Z0-9]*|"
            r"FIFO(18|36)[A-Z0-9]*|"
            r"URAM288(_[A-Z0-9]+)?|"
            r"[IO]BUF(_[A-Z0-9]+)?|"
            r"MMCME[2-4]_ADV|"
            r"PLLE[2-4]_ADV|"
            r"SRL(16|C32)[A-Z0-9]*|"
            r"CARRY[48]"
            r")$"
        ),
    ),
    # --------------------------------------------
    # ALTERA
    # --------------------------------------------
    VendorRule(
        vendor=Vendor.ALTERA,
        prefixes=(
            "altera_",
            "alt",
            "dcfifo",
            "scfifo",
            "lpm_",
        ),
        primitive_pattern=re.compile(
            r"^("
            r"dffe[a-z0-9]*|"
            r"(cyclone|stratix|arria|twentynm|fiftyfivenm|agilex)_[a-z0-9_]+"
            r")$",
            re.IGNORECASE,
        ),
    ),
    # --------------------------------------------
    # LATTICE
    # --------------------------------------------
    VendorRule(
        vendor=Vendor.LATTICE,
        prefixes=("trellis_",),
        primitive_pattern=re.compile(
            r"^("
            r"EHXPLL[A-Z0-9]*|"
            r"DP16KD|"
            r"OSCG|"
            r"FD1P3[A-Z]+|"
            r"IFS1P3[A-Z]+"
            r")$"
        ),
    ),
    # --------------------------------------------
    # MICROCHIP / MICROSEMI / ACTEL
    # --------------------------------------------
    VendorRule(
        vendor=Vendor.MICROCHIP,
        prefixes=(
            "rtg4_",
            "polarfire_",
            "core",
        ),
        primitive_pattern=re.compile(
            r"^("
            r"CLKINT|"
            r"RAM1K20|"
            r"RAM64x18|"
            r"CCC|"
            r"SLE|"
            r"DFN1[A-Z0-9]*"
            r")$"
        ),
    ),
    # --------------------------------------------
    # CADENCE
    # --------------------------------------------
    VendorRule(
        vendor=Vendor.CADENCE,
        prefixes=(
            "cw_",
            "cdn_",
            "cds_",
        ),
    ),
    # --------------------------------------------
    # SYNOPSYS
    # --------------------------------------------
    VendorRule(
        vendor=Vendor.SYNOPSYS,
        prefixes=(
            "dw_",
            "snps_",
        ),
    ),
)


def classify_vendor(entity_name: str) -> Vendor | None:
    """
    Classify the passed entity to infer the vendor, if required.
    """
    name_clean = entity_name.strip()
    name_lower = name_clean.lower()

    for rule in RULES:
        if name_lower.startswith(rule.prefixes):
            return rule.vendor

        if rule.primitive_pattern and rule.primitive_pattern.match(name_clean):
            return rule.vendor

    return None
