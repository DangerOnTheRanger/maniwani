import re

from markdown import Extension

from model.PostReplyPattern import PostReplyPattern


class PostReplyExtension(Extension):
    def extendMarkdown(self, md, _):
        post_reply = PostReplyPattern()
        md.inlinePatterns.add("post_reply", post_reply, "_begin")
        # modify the built-in blockquote regexp to only match
        # when one angle bracket is present
        # monkey patching was a mistake
        md.parser.blockprocessors["quote"].RE = re.compile(r"(^|\n)[ ]{0,3}>(?!>)[ ]?(.*)")
