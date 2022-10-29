from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain
from sphinx.domains.python import PyFunction
from sphinx.locale import _
from sphinx.util.docfields import Field, GroupedField

import re

obj_re = re.compile(
  r"""
    \[(?P<param>[A-Za-z_]+)\]
  | (?P<literal>[A-Za-z_]+)
  | (?P<punc>[\{\}^:/=\(\)\*-\|<>~\?!#&\$])
  | (?P<space>\s+)
  """,
  re.VERBOSE,
)


class PloverObject(ObjectDescription):
  has_content = True
  required_arguments = 1

  NAMESPACE_FROM_OBJTYPE = {
    "command": "cmd",
  }

  NAMESPACE_FROM_ROLE = {
    "command": "cmd",
  }

  def get_signatures(self):
    return self.arguments[0].split("; ")

  def handle_signature(self, sig, signode):
    nodes = []
    for param, literal, punc, space in obj_re.findall(sig):
      if param:
        nodes.append(addnodes.desc_sig_name("", param))
      elif literal:
        nodes.append(addnodes.desc_name("", literal))
      elif punc:
        nodes.append(addnodes.desc_addname("", punc))
      elif space:
        nodes.append(addnodes.desc_sig_space())
    signode += nodes
    return sig


class PloverCommand(PloverObject):
  def handle_signature(self, sig, signode):
    if ":" in sig:
      cmd, arg = sig.split(":", 1)
    else:
      cmd, arg = sig, None

    nodes = [
      addnodes.desc_addname("", "{plover:"),
      addnodes.desc_sig_name("", cmd)
      if cmd == "command"
      else addnodes.desc_name("", cmd),
    ]

    if arg:
      nodes += [
        addnodes.desc_addname("", ":"),
        addnodes.desc_sig_name("", arg),
      ]

    nodes += [
      addnodes.desc_addname("", "}"),
    ]
    signode += nodes
    return f"plover:{cmd}"


class PloverHook(PyFunction):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.env.ref_context["py:module"] = None

  def get_signature_prefix(self, sig):
    return [
      addnodes.desc_sig_keyword("", "hook"),
      addnodes.desc_sig_space(),
    ]


class PloverDomain(Domain):
  name = "plover"
  label = "Plover"
  directives = {
    "operator": PloverObject,
    "command": PloverCommand,
    "hook": PloverHook,
    "combo": PloverObject,
  }


def setup(app):
  app.add_domain(PloverDomain)
