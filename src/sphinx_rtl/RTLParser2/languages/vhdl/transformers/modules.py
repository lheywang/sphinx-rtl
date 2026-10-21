# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Module transformer
# ----------------------------------------------------------------------------

# Import
import re
from tree_sitter import Node

from sphinx_rtl.models import Module, Parameter
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line


def check_generate_context(inst_node, source):
    is_repeated = False
    is_conditional = False
    condition_text = ""
    count_text = ""

    current = inst_node.parent
    while current:
        if current.type == "for_generate_statement":
            is_repeated = True
            for child in current.named_children:
                if child.type == "for_loop":
                    count_text = re.split(
                        r"to|downto",
                        get_text(child, source).strip(),
                        flags=re.IGNORECASE,
                    )[-1].strip()
                    break
        elif current.type in ("if_generate_statement", "case_generate_statement"):
            is_conditional = True
            for child in current.named_children:
                if child.type not in (
                    "label_declaration",
                    "generate_body",
                    "end_generate",
                ):
                    condition_text = re.sub(
                        r"generate|if",
                        "",
                        get_text(child, source).strip().splitlines()[0],
                        flags=re.IGNORECASE,
                    ).strip()
                    break
        current = current.parent

    return is_repeated, count_text, is_conditional, condition_text


# Functions
def VHDLTransformerModule(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Module:

    # Is there anything for us ?
    if "inst.unit" in nodes:

        # Init the module and add basic elements
        module = Module()

        module.line = get_line(nodes["inst.unit"][0])
        module.name = (
            get_text(nodes["inst.unit.label"][0], source).replace(":", "").strip()
        )

        # Process the library
        entity = nodes["inst.unit.unit"][0]
        for child in entity.children:
            match child.type:
                case "name":
                    module.entity = get_text(child, source)
                case "identifier":
                    module.architecture = get_text(child, source)

        # Process the generics
        if "inst.generics" in nodes:
            assoc_list_node = nodes["inst.generics"][0]

            for child in assoc_list_node.named_children:
                if child.type == "association_element":

                    named = child.named_children

                    if len(named) >= 2:
                        formal_node = named[0]
                        actual_node = named[1]
                        f_text = get_text(formal_node, source).strip()
                        a_text = get_text(actual_node, source).strip()
                        module.params.append(
                            Parameter(
                                name=f_text, hdl_value=a_text, line=get_line(named[0])
                            )
                        )

                    elif len(named) == 1:
                        actual_node = named[0]
                        a_text = get_text(actual_node, source).strip()
                        module.params.append(
                            Parameter(hdl_value=a_text, line=get_line(named[0]))
                        )

        # Process the ports
        if "inst.ports" in nodes:
            assoc_list_node = nodes["inst.ports"][0]

            for child in assoc_list_node.named_children:
                if child.type == "association_element":

                    named = child.named_children

                    if len(named) >= 2:
                        formal_node = named[0]
                        actual_node = named[1]
                        f_text = get_text(formal_node, source).strip()
                        a_text = get_text(actual_node, source).strip()
                        module.connections.append((f_text, a_text))

                    elif len(named) == 1:
                        actual_node = named[0]
                        a_text = get_text(actual_node, source).strip()
                        module.connections.append(("", a_text))

        # Finally, handle the generate / conditions
        module.isRepeated, module.count, module.isConditionnal, module.condition = (
            check_generate_context(nodes["inst.unit"][0], source)
        )

    return Module()
