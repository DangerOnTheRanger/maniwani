# TODO: Enable \r\n to <br /> support (no more reddit spacing)
from markdown import Extension


class ThreadRootExtension(Extension):
    def extendMarkdown(self, md, _):
        md.postprocessors.add("threadroot", ThreadPostprocessor(), "_end")
