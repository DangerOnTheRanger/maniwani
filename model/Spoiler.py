import re
from markdown import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree

class SpoilerPattern(Pattern):
    _SPOILER_REGEXP = r"\|\|(.+)\|\|"
    def __init__(self, markdown_instance=None):
        super().__init__(self._SPOILER_REGEXP, markdown_instance)

    def handleMatch(self, match):
        spoiler = etree.Element("span")
        spoiler.text = match.group(2)
        spoiler.attrib["class"] = "spoiler"
        return spoiler


class SpoilerExtension(Extension):
    def extendMarkdown(self, md, _):
        spoiler = SpoilerPattern()
        md.inlinePatterns.add("spoiler", spoiler, "_begin")
