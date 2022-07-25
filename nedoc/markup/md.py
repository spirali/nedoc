import logging
import re
from typing import Optional, Tuple

import marko
from marko.inline import Link

from ..core import GlobalContext
from ..render import link_to
from ..unit import Module, Unit
from ..utils import render_cname


def dotted_to_cname(path: str) -> Tuple[str, ...]:
    return tuple(path.strip().split("."))


class NedocRenderer(marko.HTMLRenderer):
    def __init__(self, gctx: GlobalContext, unit: Unit):
        super().__init__()
        self.gctx = gctx
        self.unit = unit

    def render_link(self, element: Link) -> str:
        link = get_intradoc_link(element)
        if link is None:
            return super().render_link(element)

        original_link = link
        if link == ".":
            if isinstance(self.unit, Module):
                target = self.unit
            else:
                target = self.unit.parent
            return self.render_intradoc_link(target=target, element=element)

        # First try to resolve the link as an absolute path
        if not link.startswith("."):
            fragments = dotted_to_cname(link)
            item = self.gctx.find_by_cname(fragments)
            if item is not None:
                return self.render_intradoc_link(target=item, element=element)

            # Try to resolve the link in the same unit
            item = self.unit.local_find(link)
            if item is not None:
                return self.render_intradoc_link(target=item, element=element)

        # Then try to resolve the link as a relative path
        # Strip leading dot
        if link.startswith("."):
            link = link[1:]

        # Try to resolve the link in the same module
        parent: Unit = self.unit.module()
        if parent is not None:
            item = parent.local_find(link)
            if item is not None:
                return self.render_intradoc_link(target=item, element=element)

            # Try to resolve the link in parent modules
            # Unroll leading dots
            while link.startswith("."):
                parent = parent.parent
                if parent is None:
                    break
                link = link[1:]
            if parent is not None:
                item = parent.find_by_cname(dotted_to_cname(link), self.gctx)
                if item is not None:
                    return self.render_intradoc_link(target=item, element=element)

        logging.warning(f"Intradoc link `{original_link}` in {render_cname(self.unit.cname)} "
                        "could not be resolved")

        return super().render_link(element)

    def render_intradoc_link(self, target: Unit, element):
        url = link_to(target)
        element.dest = url
        return super().render_link(element)


# Allows dotted paths that can have an arbitrary number of dots at the beginning and at most one
# dot between alphanumeric parts
INTRADOC_LINK_REGEX = re.compile(r"\.*(?:[a-zA-z\d_]+\.?)*[a-zA-z\d_]+")


def get_intradoc_link(element: Link) -> Optional[str]:
    # The link must be wrapped in backticks [Link](`path`)
    link = element.dest.strip()
    if len(link) < 2:
        return None
    if not (link.startswith("`") and link.endswith("`")):
        return None

    link = link[1:-1]
    # The link can only consist of alphanumerical text and dots
    if link != "." and not INTRADOC_LINK_REGEX.fullmatch(link):
        return None
    return link


def convert_markdown_to_html(
        ctx: GlobalContext, unit: Unit, text: Optional[str]
) -> str:
    if text is None:
        return ""

    md = marko.Markdown()
    parsed = md.parse(text)

    # A manual way of rendering needed to pass parameters to the renderer
    renderer = NedocRenderer(gctx=ctx, unit=unit)
    renderer.root_node = parsed
    with renderer as r:
        return r.render(parsed)
