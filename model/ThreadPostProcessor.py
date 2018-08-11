from markdown.postprocessors import Postprocessor


class ThreadPostprocessor(Postprocessor):
    def run(self, text):
        return '<div class="col text-left mw-50">%s</div>' % text
