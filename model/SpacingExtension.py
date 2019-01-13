import re
from markdown import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree

class SpacingPattern(Pattern):
    _SPACING_REGEXP = r"(\r\n|\n)(?!(\r\n|\n)+)"
    def __init__(self, markdown_instance=None):
        super().__init__(self._SPACING_REGEXP, markdown_instance)

    def handleMatch(self, match):
        return etree.Element("br")


class SpacingExtension(Extension):
    def extendMarkdown(self, md, _):
        spacing = SpacingPattern()
        md.inlinePatterns.add("spacing", spacing, "_end")
