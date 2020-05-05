class Template(object):
    def __init__(self, language, extension):
        self.language = language
        self.extension = extension

    def template(self, content):
        pass


class Python(Template):
    def __init__(self):
        super().__init__(language='python', extension='.py')

    def template(self, content):
        return f'"""{content}\n\n"""\n\n\ndef answer():\n    """ Solve the problem here! """\n    return 0\n\n\nif __name__ == "__main__":\n    """ Try out your code here """\n    print(answer())\n'


class Node(Template):
    def __init__(self):
        super().__init__(language='node', extension='.js')

    def template(self, content):
        return f'/*{content}\n\n*/\n\n\nfunction answer() {{\n    // Solve the problem here!\n    return 0\n}}\n\n\n// Try out your code here \nconsole.log(answer())\n'


def get_template(language):
    for _ in Template.__subclasses__():
        template_obj = _()
        if template_obj.language == language:
            return template_obj


def supported_languages():
    return [_().language for _ in Template.__subclasses__()]
