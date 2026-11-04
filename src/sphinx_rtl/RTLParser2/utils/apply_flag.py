# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    03/11/2026
#
# Brief :   Define how to apply flags.
# ----------------------------------------------------------------------------

# Imports
import shlex

from sphinx_rtl.models import ComponentConfig
from sphinx_rtl.RTLConfig import RTLConfig


# Define helper functions
def _str(field):
    def h(cfg, args):
        setattr(cfg, field, args)

    return h


def _int(field):
    def h(cfg, args):
        setattr(cfg, field, int(args))

    return h


def _append(field):
    def h(cfg, args):
        getattr(cfg, field).append(args)

    return h


def _testbench(cfg, args):
    cfg.isTestbench = True
    cfg.testbenchTarget = args


def _clock(cfg, args):
    name, freq, *rest = shlex.split(args)
    cfg.clock.append((name, freq, rest[0] if rest else ""))


def _register(cfg, args):
    name, addr, width, *rest = shlex.split(args)
    cfg.register.append(
        (name, int(addr, 0), int(width), " ".join(rest) if rest else "")
    )


# Flags LUT
FLAGS = {
    "warning": _append("warning"),
    "note": _append("notes"),
    "target": _append("target"),
    "tool": _append("tool"),
    "sim": _append("sim"),
    "compliance": _append("compliance"),
    "throughput": _str("throughput"),
    "security": _str("security"),
    "deprecated": _str("deprecated"),
    "task": _str("task"),
    "license": _append("license"),
    "copyright": _str("copyright"),
    "version": _str("version"),
    "status": _str("status"),
    "latency": _int("latency"),
    "burst": _int("burst"),
    "constraint": _append("constraints"),
    "tag": _append("tags"),
    "testbench": _testbench,
    "package": lambda cfg, a: setattr(cfg, "isPackage", True),
    "interface": lambda cfg, a: setattr(cfg, "isInterface", True),
    "clock": _clock,
    "register": _register,
}

NEGATIVE_FLAGS = {
    "noclocks": "inferClocks",
    "noresets": "inferResets",
    "noio": "inferIOs",
    "notype": "inferType",
    "nopolarity": "inferPolarity",
    "nogroups": "inferGroups",
    "noassigns": "inferAssignments",
    "noresolve": "resolveModules",
    "nosource": "showSource",
    "notemplate": "template",
    "nosignals": "signals",
    "nointernals": "internals",
    "novendors": "inferVendor",
}


def apply_flags_cfg(cfg: ComponentConfig, flags: list[dict]) -> list[str]:
    """
    Apply the flags for the configuration of the component.
    """
    errors = []
    for f in flags:
        handler = FLAGS.get(f["name"])
        if handler is None:
            continue
        try:
            handler(cfg, f["args"])
            cfg.changed = True
        except (ValueError, TypeError):
            errors.append(
                f"line {f['line']}: bad arguments for @{f['name']}: {f['args']!r}"
            )
    return errors


def apply_flags_render(cfg: RTLConfig, flags: list[dict]) -> list[str]:
    """
    Apply the flags for the rendering pass.
    """
    warnings = []
    for f in flags:
        name, args, line = f["name"], f["args"], f["line"]

        if name in NEGATIVE_FLAGS:
            if args:
                warnings.append(
                    f"line {line}: @{name} takes no argument, ignored: {args!r}"
                )
            setattr(cfg, NEGATIVE_FLAGS[name], False)

        elif name == "vendor":
            names = args.replace(",", " ").split()
            if not names:
                warnings.append(f"line {line}: @vendor needs at least one name")
            for n in names:
                if n not in cfg.vendor:
                    cfg.vendor.append(n)

    return warnings
