def get_template(language):
    for _ in Template.__subclasses__():
        template_obj = _()
        if template_obj.language == language:
            return template_obj


def supported_languages():
    return [_().language for _ in Template.__subclasses__()]


class Template(object):
    def __init__(self, language, extension):
        self.language = language
        self.extension = extension

    def template(self, content):
        pass


class Python(Template):
    def __init__(self):
        super().__init__(language='python3', extension='.py')

    def template(self, content):
        return f'"""{content}\n\n"""\n\n\ndef answer():\n    """ Solve the problem here! Make sure to return the answer. """\n    return 0\n\n\nif __name__ == "__main__":\n    """ Below is OK to leave alone """\n    print(answer())\n'


class Node(Template):
    def __init__(self):
        super().__init__(language='node', extension='.js')

    def template(self, content):
        return f'/*{content}\n\n*/\n\n\nfunction answer() {{\n    // Solve the problem here! Make sure to return the answer. \n    return 0\n}}\n\n\n// Below is OK to leave alone\nconsole.log(answer())\n'


class Ruby(Template):
    def __init__(self):
        super().__init__(language='ruby', extension='.rb')

    def template(self, content):
        return f'<<-DOC\n{content}\n\nDOC\n\n\ndef answer()\n    # Solve the problem here! Make sure to return the answer.\n    return 0\nend\n\n\n# Below is OK to leave alone\n puts answer()'
